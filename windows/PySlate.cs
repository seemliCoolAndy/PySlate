using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading.Tasks;
using System.Web.Script.Serialization;
using System.Windows.Forms;
using Microsoft.Web.WebView2.Core;
using Microsoft.Web.WebView2.WinForms;

namespace PySlate {
    static class Program {
        internal static string[] Arguments;
        [STAThread] static void Main(string[] args) {
            Arguments = args;
            try { SetProcessDPIAware(); } catch { }
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new MainWindow());
        }
        [DllImport("user32.dll")] static extern bool SetProcessDPIAware();
        [DllImport("user32.dll")] static extern uint GetDpiForSystem();
        internal static float DpiScale() { try { return GetDpiForSystem() / 96f; } catch { return 1; } }
        internal static string Option(string name, string fallback) {
            for (int i = 0; i < Arguments.Length - 1; i++) if (Arguments[i] == name) return Arguments[i + 1];
            return fallback;
        }
    }
    sealed class MainWindow : Form {
        WebView2 browser;
        Process backend;
        IntPtr job;
        string origin;
        bool closeApproved, closePending;
        string flushId;
        TaskCompletionSource<bool> flushCompletion;
        readonly Label loading;
        void Log(string text) { string path = Program.Option("--capture", null); if (path != null) File.AppendAllText(path + ".log", DateTime.Now.ToString("O") + " " + text + "\n", Encoding.UTF8); }
        void OpenOfficial(string address, bool userInitiated) {
            Uri destination;
            if (userInitiated && Uri.TryCreate(address, UriKind.Absolute, out destination) && destination.Scheme == "https" &&
                (destination.Host == "docs.python.org" || destination.Host == "www.python.org" || destination.Host == "python.org"))
                Process.Start(new ProcessStartInfo(destination.AbsoluteUri) { UseShellExecute = true });
        }
        public MainWindow() {
            Text = "PySlate — Python 学习与编程";
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
            float scale = Program.DpiScale();
            Rectangle available = Screen.PrimaryScreen.WorkingArea;
            Width = Math.Min((int)(Int32.Parse(Program.Option("--width", "1380")) * scale), available.Width - (int)(24 * scale));
            Height = Math.Min((int)(Int32.Parse(Program.Option("--height", "900")) * scale), available.Height - (int)(24 * scale));
            MinimumSize = new Size((int)(320 * scale), Math.Min((int)(400 * scale), available.Height));
            StartPosition = FormStartPosition.CenterScreen;
            BackColor = Color.FromArgb(245, 245, 239);
            loading = new Label { Text = "PySlate\n正在打开你的编程手册…", Dock = DockStyle.Fill, TextAlign = ContentAlignment.MiddleCenter, Font = new Font("Microsoft YaHei UI", 18) };
            Controls.Add(loading);
            Shown += async delegate { await Start(); };
            FormClosing += async delegate(object sender, FormClosingEventArgs e) {
                if (closeApproved || browser == null || browser.CoreWebView2 == null) return;
                e.Cancel = true;
                if (closePending) return;
                closePending = true;
                bool saved = false;
                try {
                    flushId = Guid.NewGuid().ToString("N");
                    flushCompletion = new TaskCompletionSource<bool>();
                    await browser.ExecuteScriptAsync("Promise.resolve(window.pyslateFlush && window.pyslateFlush()).then(function(){window.chrome.webview.postMessage({type:'pyslate-flush',id:'" + flushId + "',ok:true})}).catch(function(){window.chrome.webview.postMessage({type:'pyslate-flush',id:'" + flushId + "',ok:false})})");
                    if (await Task.WhenAny(flushCompletion.Task, Task.Delay(5000)) == flushCompletion.Task) saved = await flushCompletion.Task;
                } catch { }
                Log("close flush confirmed=" + saved);
                if (saved || MessageBox.Show(this, "最后的编辑尚未确认保存。建议返回编辑器并按 Ctrl+S 重试。\n\n仍然退出？", "有内容尚未保存", MessageBoxButtons.YesNo, MessageBoxIcon.Warning, MessageBoxDefaultButton.Button2) == DialogResult.Yes) {
                    closeApproved = true; Close();
                } else closePending = false;
            };
            FormClosed += delegate { CloseBackend(); };
        }
        async Task Start() {
            try {
                Log("starting host");
                string root = AppDomain.CurrentDomain.BaseDirectory;
                string data = Path.GetFullPath(Program.Option("--data", Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "PySlate", "Data")));
                Directory.CreateDirectory(data);
                string runtimeVersion = CoreWebView2Environment.GetAvailableBrowserVersionString();
                var info = new ProcessStartInfo(Path.Combine(root, "python", "python.exe"));
                info.Arguments = "-u -X utf8 \"" + Path.Combine(root, "runtime", "server.py") + "\" --root \"" + root.TrimEnd('\\') + "\" --data \"" + data + "\"";
                info.WorkingDirectory = root;
                info.UseShellExecute = false;
                info.CreateNoWindow = true;
                info.RedirectStandardOutput = true;
                info.RedirectStandardError = true;
                info.StandardOutputEncoding = Encoding.UTF8;
                info.StandardErrorEncoding = Encoding.UTF8;
                backend = Process.Start(info);
                job = Job.Create(backend);
                string backendError = "";
                backend.ErrorDataReceived += delegate(object s, DataReceivedEventArgs e) { if (e.Data != null) backendError += e.Data + "\n"; };
                backend.BeginErrorReadLine();
                Task<string> readyTask = backend.StandardOutput.ReadLineAsync();
                if (await Task.WhenAny(readyTask, Task.Delay(15000)) != readyTask) throw new Exception("本地 Python 服务启动超时。");
                string line = await readyTask;
                Log("backend ready");
                if (String.IsNullOrEmpty(line)) throw new Exception("Python 服务未能启动。\n" + backendError);
                var ready = new JavaScriptSerializer().Deserialize<System.Collections.Generic.Dictionary<string, object>>(line);
                string url = (string)ready["url"];
                origin = new Uri(url).GetLeftPart(UriPartial.Authority);
                string readyFile = Program.Option("--ready-file", null);
                if (readyFile != null) File.WriteAllText(readyFile, line, Encoding.UTF8);
                browser = new WebView2 { Dock = DockStyle.Fill };
                Controls.Add(browser);
                browser.BringToFront();
                var environment = await CoreWebView2Environment.CreateAsync(null, Path.Combine(data, "WebView2"), null);
                Log("environment ready");
                await browser.EnsureCoreWebView2Async(environment);
                Log("webview ready");
                browser.CoreWebView2.Settings.IsStatusBarEnabled = false;
                browser.CoreWebView2.Settings.AreDevToolsEnabled = false;
                browser.CoreWebView2.Settings.AreDefaultContextMenusEnabled = false;
                browser.CoreWebView2.Settings.IsWebMessageEnabled = true;
                browser.CoreWebView2.Settings.AreHostObjectsAllowed = false;
                browser.CoreWebView2.WebMessageReceived += delegate(object s, CoreWebView2WebMessageReceivedEventArgs e) {
                    try {
                        if (!e.Source.StartsWith(origin + "/", StringComparison.Ordinal) || flushCompletion == null) return;
                        var message = new JavaScriptSerializer().Deserialize<System.Collections.Generic.Dictionary<string, object>>(e.WebMessageAsJson);
                        if ((string)message["type"] == "pyslate-flush" && (string)message["id"] == flushId) flushCompletion.TrySetResult((bool)message["ok"]);
                    } catch { }
                };
                browser.CoreWebView2.PermissionRequested += delegate(object s, CoreWebView2PermissionRequestedEventArgs e) { e.State = CoreWebView2PermissionState.Deny; };
                browser.CoreWebView2.NavigationStarting += delegate(object s, CoreWebView2NavigationStartingEventArgs e) {
                    if (!e.Uri.StartsWith(origin + "/", StringComparison.Ordinal) && e.Uri != "about:blank") { e.Cancel = true; OpenOfficial(e.Uri, e.IsUserInitiated); }
                };
                browser.CoreWebView2.NewWindowRequested += delegate(object s, CoreWebView2NewWindowRequestedEventArgs e) {
                    e.Handled = true;
                    OpenOfficial(e.Uri, e.IsUserInitiated);
                };
                browser.CoreWebView2.NavigationCompleted += async delegate(object s, CoreWebView2NavigationCompletedEventArgs e) {
                    Log("navigation completed success=" + e.IsSuccess + " status=" + e.WebErrorStatus);
                    loading.Visible = false;
                    string capture = Program.Option("--capture", null);
                    if (capture != null) {
                        await Task.Delay(Int32.Parse(Program.Option("--capture-delay", "3000")));
                        string script = Program.Option("--capture-script", null);
                        if (script != null) { await browser.ExecuteScriptAsync(File.ReadAllText(script)); await Task.Delay(Int32.Parse(Program.Option("--capture-script-wait", "800"))); }
                        File.WriteAllText(capture + ".json", await browser.ExecuteScriptAsync("({title:document.title,width:innerWidth,height:innerHeight,visibility:document.visibilityState,overflow:document.documentElement.scrollWidth>innerWidth,brokenImages:Array.from(document.images).filter(function(i){return i.complete&&!i.naturalWidth}).map(function(i){return i.getAttribute('src')}),text:document.body.innerText.slice(0,3000)})"), Encoding.UTF8);
                        Log("DOM captured");
                        // Chromium's screenshot protocol is also usable on machines
                        // where CapturePreviewAsync stalls in the graphics driver.
                        Task<string> screenshot = browser.CoreWebView2.CallDevToolsProtocolMethodAsync("Page.captureScreenshot", "{\"format\":\"png\",\"captureBeyondViewport\":false}");
                        if (await Task.WhenAny(screenshot, Task.Delay(10000)) != screenshot) throw new Exception("WebView2 截图超时；请保留窗口并人工检查。");
                        var pixels = new JavaScriptSerializer { MaxJsonLength = 32 * 1024 * 1024 }.Deserialize<System.Collections.Generic.Dictionary<string, object>>(await screenshot);
                        File.WriteAllBytes(capture, Convert.FromBase64String((string)pixels["data"]));
                        Log("pixels captured");
                        Close();
                    }
                };
                browser.Source = new Uri(url);
            } catch (WebView2RuntimeNotFoundException) {
                MessageBox.Show(this, "需要 Microsoft Edge WebView2 Runtime 才能显示界面。Windows 11 与已更新的 Windows 10 通常已包含此组件。\n\n请从 Microsoft 官方网站安装免费 WebView2 Runtime，然后重新打开 PySlate。Python 已随软件提供。", "缺少显示组件", MessageBoxButtons.OK, MessageBoxIcon.Information);
                Close();
            } catch (Exception error) {
                Log("error: " + error);
                MessageBox.Show(this, error.Message, "PySlate 无法启动", MessageBoxButtons.OK, MessageBoxIcon.Error);
                Close();
            }
        }
        void CloseBackend() {
            if (job != IntPtr.Zero) { Job.CloseHandle(job); job = IntPtr.Zero; }
            if (backend != null) { try { if (!backend.HasExited) backend.Kill(); } catch { } backend.Dispose(); backend = null; }
            if (browser != null) { browser.Dispose(); browser = null; }
        }
    }
    static class Job {
        [StructLayout(LayoutKind.Sequential)] struct Basic { public long a, b; public uint flags; public UIntPtr min, max; public uint active; public UIntPtr affinity; public uint priority, scheduling; }
        [StructLayout(LayoutKind.Sequential)] struct Io { public ulong a, b, c, d, e, f; }
        [StructLayout(LayoutKind.Sequential)] struct Extended { public Basic basic; public Io io; public UIntPtr processMemory, jobMemory, peakProcess, peakJob; }
        [DllImport("kernel32.dll", CharSet = CharSet.Unicode)] static extern IntPtr CreateJobObject(IntPtr security, string name);
        [DllImport("kernel32.dll")] static extern bool SetInformationJobObject(IntPtr job, int kind, IntPtr data, uint size);
        [DllImport("kernel32.dll")] static extern bool AssignProcessToJobObject(IntPtr job, IntPtr process);
        [DllImport("kernel32.dll")] internal static extern bool CloseHandle(IntPtr handle);
        internal static IntPtr Create(Process process) {
            IntPtr handle = CreateJobObject(IntPtr.Zero, null);
            Extended limits = new Extended(); limits.basic.flags = 0x2000;
            int size = Marshal.SizeOf(limits); IntPtr pointer = Marshal.AllocHGlobal(size);
            try {
                Marshal.StructureToPtr(limits, pointer, false);
                if (handle == IntPtr.Zero || !SetInformationJobObject(handle, 9, pointer, (uint)size) || !AssignProcessToJobObject(handle, process.Handle)) {
                    if (handle != IntPtr.Zero) CloseHandle(handle);
                    process.Kill(); throw new Exception("无法建立应用进程组。");
                }
                return handle;
            } finally { Marshal.FreeHGlobal(pointer); }
        }
    }
}
