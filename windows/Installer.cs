using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Threading.Tasks;
using System.Windows.Forms;
using Microsoft.Win32;

namespace PySlateSetup {
    static class Program {
        public static string[] Args;
        public static string Option(string key, string fallback) { int i = Array.IndexOf(Args, key); return i >= 0 && i + 1 < Args.Length ? Args[i + 1] : fallback; }
        public static bool Has(string key) { return Array.IndexOf(Args, key) >= 0; }
        [DllImport("user32.dll")] static extern uint GetDpiForSystem();
        public static void ScaleWindow(Form window) {
            float factor = 1;
            try { factor = GetDpiForSystem() / 96f; } catch { }
            Rectangle screen = Screen.PrimaryScreen.WorkingArea;
            foreach (Control control in window.Controls) control.Bounds = new Rectangle((int)(control.Left * factor), (int)(control.Top * factor), (int)(control.Width * factor), (int)(control.Height * factor));
            window.Size = new Size(Math.Min((int)(window.Width * factor), screen.Width), Math.Min((int)(window.Height * factor), screen.Height));
        }
        [STAThread] static int Main(string[] args) {
            Args = args;
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            if (Has("--silent")) {
                try { if (!Has("--accept-webview2-license")) throw new Exception("Silent installation requires --accept-webview2-license after reviewing the included Microsoft terms."); Install(Option("--target", DefaultTarget), !Has("--no-shortcuts"), !Has("--portable-test"), null); return 0; }
                catch (Exception e) { string report = Option("--report", null); if (report != null) File.WriteAllText(report, e.ToString()); return 1; }
            }
            Application.Run(new SetupWindow()); return 0;
        }
        public static string DefaultTarget { get { return Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "Programs", "PySlate"); } }
        public static void Install(string target, bool shortcuts, bool register, Action<int> progress) {
            target = Path.GetFullPath(target).TrimEnd(Path.DirectorySeparatorChar);
            string marker = Path.Combine(target, "pyslate.install");
            if (Directory.Exists(target) && Directory.GetFileSystemEntries(target).Length > 0 && (!File.Exists(marker) || (File.ReadAllText(marker) != "PySlate 0.1" && File.ReadAllText(marker) != "PySlate 0.2" && File.ReadAllText(marker) != "PySlate 0.3")))
                throw new InvalidOperationException("目标目录中已有其他文件。请选择空目录，或现有的 PySlate 安装目录。");
            for (DirectoryInfo current = new DirectoryInfo(target); current != null; current = current.Parent)
                if (current.Exists && (current.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("安装路径不能包含链接或重解析点。");
            string stage = target + ".stage-" + Guid.NewGuid().ToString("N");
            string rollback = target + ".rollback-" + Guid.NewGuid().ToString("N");
            Directory.CreateDirectory(stage);
            var installed = new List<string>();
            var changed = new List<string>();
            var createdDirectories = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            try {
                using (Stream resource = Assembly.GetExecutingAssembly().GetManifestResourceStream("PySlate.payload.zip"))
                using (ZipArchive zip = new ZipArchive(resource, ZipArchiveMode.Read)) {
                    int count = 0;
                    foreach (ZipArchiveEntry entry in zip.Entries) {
                        if (String.IsNullOrEmpty(entry.Name)) continue;
                        string relative = entry.FullName.Replace('/', Path.DirectorySeparatorChar);
                        string destination = Path.GetFullPath(Path.Combine(stage, relative));
                        if (!destination.StartsWith(stage + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("安装包路径无效。");
                        Directory.CreateDirectory(Path.GetDirectoryName(destination));
                        using (Stream input = entry.Open()) using (Stream output = File.Create(destination)) input.CopyTo(output);
                        installed.Add(relative);
                        if (progress != null) progress(++count * 85 / zip.Entries.Count);
                    }
                }
                File.WriteAllText(Path.Combine(stage, "pyslate.install"), "PySlate 0.3");
                installed.Add("pyslate.install");
                installed.Add("install-manifest.txt");
                File.WriteAllLines(Path.Combine(stage, "install-manifest.txt"), installed);
                // Validate every existing destination before changing any file.
                // An existing installation can contain user-created links inside it.
                foreach (string relative in installed) ValidateDestination(target, relative);
                // Retain the previous bytes until the entire update succeeds.
                // Copying remains compatible with managed Windows filesystems
                // which may deny renaming populated installation directories.
                CreateDirectories(target, createdDirectories);
                foreach (string relative in installed) {
                    string destination = Path.Combine(target, relative);
                    CreateDirectories(Path.GetDirectoryName(destination), createdDirectories);
                    if (File.Exists(destination)) {
                        string previous = Path.Combine(rollback, relative);
                        Directory.CreateDirectory(Path.GetDirectoryName(previous));
                        File.Copy(destination, previous, false);
                    }
                    changed.Add(relative);
                    File.Copy(Path.Combine(stage, relative), destination, true);
                }
                EnsureWebViewRuntime(target);
                if (shortcuts) {
                    MakeShortcut(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory), "PySlate.lnk"), target);
                    MakeShortcut(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Programs), "PySlate.lnk"), target);
                }
                if (register) using (RegistryKey key = Registry.CurrentUser.CreateSubKey(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\PySlate")) {
                    key.SetValue("DisplayName", "PySlate — Python 学习与编程"); key.SetValue("DisplayVersion", "0.3.0");
                    key.SetValue("Publisher", "PySlate contributors"); key.SetValue("InstallLocation", target);
                    key.SetValue("DisplayIcon", Path.Combine(target, "PySlate.exe"));
                    key.SetValue("UninstallString", "\"" + Path.Combine(target, "Uninstall.exe") + "\"");
                    key.SetValue("NoModify", 1); key.SetValue("NoRepair", 1);
                }
                if (progress != null) progress(100);
            } catch (Exception installError) {
                Exception restoreError = null;
                foreach (string relative in changed.AsEnumerable().Reverse()) {
                    try {
                        string destination = Path.Combine(target, relative);
                        string previous = Path.Combine(rollback, relative);
                        if (File.Exists(previous)) {
                            // A sharing violation can reject a write before it
                            // changes anything; leave that still-locked file alone.
                            if (!SameContents(previous, destination)) File.Copy(previous, destination, true);
                        } else if (File.Exists(destination)) File.Delete(destination);
                    } catch (Exception error) { restoreError = restoreError ?? error; }
                }
                foreach (string directory in createdDirectories.OrderByDescending(p => p.Length)) {
                    try { if (Directory.Exists(directory) && Directory.GetFileSystemEntries(directory).Length == 0) Directory.Delete(directory, false); }
                    catch (Exception error) { restoreError = restoreError ?? error; }
                }
                if (restoreError != null) throw new IOException("安装未完成，部分文件暂时无法恢复。旧文件备份已保留在 " + rollback + "。请关闭占用程序后重试。", installError);
                if (Directory.Exists(rollback)) DeleteStage(rollback);
                throw;
            } finally { if (Directory.Exists(stage)) DeleteStage(stage); }
            if (Directory.Exists(rollback)) DeleteStage(rollback);
        }
        static void ValidateDestination(string root, string relative) {
            string destination = Path.GetFullPath(Path.Combine(root, relative));
            if (!destination.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new InvalidDataException("安装包路径无效。");
            if (File.Exists(destination) && (File.GetAttributes(destination) & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("安装文件不能是链接或重解析点。");
            for (DirectoryInfo current = new DirectoryInfo(Path.GetDirectoryName(destination)); current != null; current = current.Parent)
                if (current.Exists && (current.Attributes & FileAttributes.ReparsePoint) != 0) throw new InvalidOperationException("安装路径不能包含链接或重解析点。");
        }
        static void CreateDirectories(string path, HashSet<string> created) {
            for (DirectoryInfo current = new DirectoryInfo(path); current != null && !current.Exists; current = current.Parent) created.Add(current.FullName);
            Directory.CreateDirectory(path);
        }
        static bool SameContents(string first, string second) {
            if (!File.Exists(second) || new FileInfo(first).Length != new FileInfo(second).Length) return false;
            using (Stream a = File.OpenRead(first)) using (Stream b = File.OpenRead(second)) {
                byte[] left = new byte[65536], right = new byte[65536];
                int read;
                while ((read = a.Read(left, 0, left.Length)) != 0) {
                    int offset = 0;
                    while (offset < read) { int count = b.Read(right, offset, read - offset); if (count == 0) return false; offset += count; }
                    for (int i = 0; i < read; i++) if (left[i] != right[i]) return false;
                }
                return b.ReadByte() == -1;
            }
        }
        static void EnsureWebViewRuntime(string target) {
            if (HasWebViewRuntime()) return;
            string runtime = Path.Combine(target, "redist", "MicrosoftEdgeWebView2RuntimeInstallerX64.exe");
            if (!File.Exists(runtime) || new FileInfo(runtime).Length < 50 * 1024 * 1024) throw new Exception("缺少完整的 WebView2 离线安装器。");
            using (var process = Process.Start(new ProcessStartInfo(runtime, "/silent /install") { UseShellExecute = false, CreateNoWindow = true, WindowStyle = ProcessWindowStyle.Hidden })) {
                if (!process.WaitForExit(180000)) throw new Exception("WebView2 离线安装尚未完成，请稍后重新运行安装程序。");
                if (!HasWebViewRuntime()) throw new Exception("Microsoft WebView2 安装未成功（退出码 " + process.ExitCode + "）。请检查系统安装策略；原始离线安装器已保留在 redist 文件夹。");
            }
        }
        static bool HasWebViewRuntime() {
            const string client = @"Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}";
            foreach (var item in new[] { new { Hive = Registry.CurrentUser, Path = @"Software\" + client }, new { Hive = Registry.LocalMachine, Path = @"SOFTWARE\WOW6432Node\" + client }, new { Hive = Registry.LocalMachine, Path = @"SOFTWARE\" + client } }) {
                using (RegistryKey key = item.Hive.OpenSubKey(item.Path)) {
                    if (key == null) continue;
                    Version version;
                    if (Version.TryParse(Convert.ToString(key.GetValue("pv", "")), out version) && version.Major >= 110) return true;
                }
            }
            return false;
        }
        static void DeleteStage(string path) {
            // This path is freshly created by this installer and contains only verified embedded entries.
            foreach (string file in Directory.GetFiles(path, "*", SearchOption.AllDirectories)) File.Delete(file);
            foreach (string dir in Directory.GetDirectories(path, "*", SearchOption.AllDirectories).OrderByDescending(p => p.Length)) Directory.Delete(dir, false);
            Directory.Delete(path, false);
        }
        static void MakeShortcut(string path, string target) {
            dynamic shell = Activator.CreateInstance(Type.GetTypeFromProgID("WScript.Shell"));
            dynamic link = shell.CreateShortcut(path);
            string existing = link.TargetPath;
            if (File.Exists(path) && !String.Equals(existing, Path.Combine(target, "PySlate.exe"), StringComparison.OrdinalIgnoreCase)) return;
            link.TargetPath = Path.Combine(target, "PySlate.exe"); link.WorkingDirectory = target; link.Description = "离线 Python 学习与编程"; link.Save();
        }
    }
    sealed class SetupWindow : Form {
        TextBox destination;
        Button install;
        ProgressBar progress;
        CheckBox shortcut, launch, agreement;
        Label status;
        public SetupWindow() {
            Text = "安装 PySlate"; Width = 660; Height = 550; FormBorderStyle = FormBorderStyle.FixedDialog;
            try { Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
            MaximizeBox = false; StartPosition = FormStartPosition.CenterScreen; BackColor = Color.FromArgb(245, 245, 239);
            Font = new Font("Microsoft YaHei UI", 10);
            Controls.Add(new Label { Text = "PySlate", Font = new Font("Segoe UI", 30, FontStyle.Bold), Left = 34, Top = 25, Width = 550, Height = 60, ForeColor = Color.FromArgb(42, 71, 62) });
            Controls.Add(new Label { Text = "一本可以运行代码的 Python 学习手册", Left = 38, Top = 92, Width = 550, Height = 28 });
            Controls.Add(new Label { Text = "免费 · 无广告 · 无需登录 · 内置 Python 3.13", Left = 38, Top = 125, Width = 550, Height = 28 });
            Controls.Add(new Label { Text = "安装位置（当前用户，无需管理员权限）", Left = 38, Top = 170, Width = 540, Height = 27 });
            destination = new TextBox { Text = Program.Option("--target", Program.DefaultTarget), Left = 38, Top = 200, Width = 490 };
            Controls.Add(destination);
            Button browse = new Button { Text = "浏览", Left = 540, Top = 198, Width = 70, Height = 30 };
            browse.Click += delegate { using (var dialog = new FolderBrowserDialog()) { if (dialog.ShowDialog(this) == DialogResult.OK) destination.Text = Path.Combine(dialog.SelectedPath, "PySlate"); } };
            Controls.Add(browse);
            shortcut = new CheckBox { Text = "创建桌面与开始菜单快捷方式", Checked = true, Left = 38, Top = 245, Width = 540, Height = 26 }; Controls.Add(shortcut);
            launch = new CheckBox { Text = "安装完成后打开 PySlate", Checked = true, Left = 38, Top = 274, Width = 540, Height = 26 }; Controls.Add(launch);
            agreement = new CheckBox { Text = "我同意 Microsoft WebView2 Runtime 许可条款", Left = 38, Top = 310, Width = 465, Height = 28 }; Controls.Add(agreement);
            var terms = new LinkLabel { Text = "阅读条款", Left = 520, Top = 315, Width = 90, Height = 28 }; Controls.Add(terms);
            terms.LinkClicked += delegate { using (var window = new Form { Text = "Microsoft WebView2 Runtime 许可条款", Width = 800, Height = 650, StartPosition = FormStartPosition.CenterParent }) { var text = new TextBox { Multiline = true, ReadOnly = true, ScrollBars = ScrollBars.Vertical, Dock = DockStyle.Fill, Font = new Font("Segoe UI", 10) }; using (var stream = Assembly.GetExecutingAssembly().GetManifestResourceStream("PySlate.WebView2License.txt")) using (var reader = new StreamReader(stream)) text.Text = reader.ReadToEnd(); window.Controls.Add(text); Program.ScaleWindow(window); window.ShowDialog(this); } };
            Controls.Add(new Label { Text = "仅缺少组件时使用随附离线安装器。WebView2 可能自行更新或向 Microsoft 发送诊断信息；含 SmartScreen。隐私条款见许可证。", Left = 38, Top = 345, Width = 570, Height = 48, ForeColor = Color.DimGray });
            status = new Label { Text = "项目和练习独立保存，升级保留数据。", Left = 38, Top = 402, Width = 570, Height = 27 }; Controls.Add(status);
            progress = new ProgressBar { Left = 38, Top = 448, Width = 400, Height = 22 }; Controls.Add(progress);
            install = new Button { Text = "安装", Enabled = false, Left = 470, Top = 440, Width = 140, Height = 40, BackColor = Color.FromArgb(42, 71, 62), ForeColor = Color.White, FlatStyle = FlatStyle.Flat }; Controls.Add(install);
            agreement.CheckedChanged += delegate { install.Enabled = agreement.Checked; };
            install.Click += async delegate {
                string target = destination.Text;
                install.Enabled = destination.Enabled = browse.Enabled = false;
                bool shortcuts = shortcut.Checked;
                status.Text = "正在安装 Python 与离线课程…";
                try {
                    await Task.Run(delegate { Program.Install(target, shortcuts, true, delegate(int value) { BeginInvoke((Action)(delegate { progress.Value = value; })); }); });
                    if (launch.Checked) Process.Start(new ProcessStartInfo(Path.Combine(target, "PySlate.exe")) { UseShellExecute = true });
                    Close();
                } catch (Exception error) { MessageBox.Show(this, error.Message, "安装未完成", MessageBoxButtons.OK, MessageBoxIcon.Error); install.Enabled = destination.Enabled = browse.Enabled = true; status.Text = "请关闭已运行的 PySlate 后重试。"; }
            };
            Program.ScaleWindow(this);
            string capture = Program.Option("--capture", null);
            if (capture != null) Shown += async delegate { await Task.Delay(500); using (var bitmap = new Bitmap(ClientSize.Width, ClientSize.Height)) { DrawToBitmap(bitmap, new Rectangle(0, 0, ClientSize.Width, ClientSize.Height)); bitmap.Save(capture, System.Drawing.Imaging.ImageFormat.Png); } Close(); };
        }
    }
}
