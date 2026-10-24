using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Windows.Forms;
using Microsoft.Win32;

static class Uninstall {
    [STAThread] static int Main(string[] args) {
        Application.EnableVisualStyles();
        try {
            string root = AppDomain.CurrentDomain.BaseDirectory.TrimEnd(Path.DirectorySeparatorChar);
            bool removing = args.Length >= 2 && args[0] == "--remove";
            bool test = args.Contains("--portable-test");
            if (removing) root = Path.GetFullPath(args[1]).TrimEnd(Path.DirectorySeparatorChar);
            if (!File.Exists(Path.Combine(root, "pyslate.install"))) throw new Exception("这不是有效的 PySlate 安装目录。");
            string marker = File.ReadAllText(Path.Combine(root, "pyslate.install"));
            if (marker != "PySlate 0.1" && marker != "PySlate 0.2" && marker != "PySlate 0.3") throw new Exception("这不是有效的 PySlate 安装目录。");
            if (!removing) {
                if (!args.Contains("--silent") && MessageBox.Show("卸载 PySlate？\n\n你的项目、课程进度与练习将保留在 LocalAppData\\PySlate\\Data。", "卸载 PySlate", MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes) return 0;
                string helper = Path.Combine(Path.GetTempPath(), "PySlate-Uninstall-" + Guid.NewGuid().ToString("N") + ".exe");
                File.Copy(Assembly.GetExecutingAssembly().Location, helper);
                var process = Process.Start(new ProcessStartInfo(helper, "--remove \"" + root + "\"" + (test ? " --portable-test" : "")) { UseShellExecute = false, CreateNoWindow = true });
                return 0;
            }
            System.Threading.Thread.Sleep(750);
            string manifest = Path.Combine(root, "install-manifest.txt");
            var entries = File.ReadAllLines(manifest);
            var applicationDirectories = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { root };
            foreach (string relative in entries) {
                if (relative == "install-manifest.txt" || relative == "pyslate.install") continue;
                string path = Path.GetFullPath(Path.Combine(root, relative));
                if (!path.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)) throw new Exception("卸载清单包含无效路径。");
                var directory = new DirectoryInfo(Path.GetDirectoryName(path));
                for (var current = directory; current != null && (current.FullName.Equals(root, StringComparison.OrdinalIgnoreCase) || current.FullName.StartsWith(root + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)); current = current.Parent) {
                    if (current.Exists && (current.Attributes & FileAttributes.ReparsePoint) != 0) throw new Exception("卸载路径包含链接，请手动处理。");
                    applicationDirectories.Add(current.FullName);
                }
                if (File.Exists(path)) File.Delete(path);
            }
            File.Delete(manifest); File.Delete(Path.Combine(root, "pyslate.install"));
            // Only inspect parents of listed application files. Recursive
            // enumeration would follow unlisted junctions and could remove
            // empty learner directories outside this installation.
            foreach (string directory in applicationDirectories.OrderByDescending(p => p.Length))
                if (Directory.Exists(directory) && (File.GetAttributes(directory) & FileAttributes.ReparsePoint) == 0 && Directory.GetFileSystemEntries(directory).Length == 0) Directory.Delete(directory, false);
            if (!test) {
                Registry.CurrentUser.DeleteSubKeyTree(@"Software\Microsoft\Windows\CurrentVersion\Uninstall\PySlate", false);
                foreach (string folder in new[] { Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory), Environment.GetFolderPath(Environment.SpecialFolder.Programs) }) {
                    string shortcut = Path.Combine(folder, "PySlate.lnk");
                    if (!File.Exists(shortcut)) continue;
                    dynamic shell = Activator.CreateInstance(Type.GetTypeFromProgID("WScript.Shell")); dynamic link = shell.CreateShortcut(shortcut);
                    if (String.Equals((string)link.TargetPath, Path.Combine(root, "PySlate.exe"), StringComparison.OrdinalIgnoreCase)) File.Delete(shortcut);
                }
            }
            return 0;
        } catch (Exception error) { MessageBox.Show(error.Message, "卸载未完成", MessageBoxButtons.OK, MessageBoxIcon.Warning); return 1; }
    }
}
