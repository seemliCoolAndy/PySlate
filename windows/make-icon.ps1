param([string]$Destination = (Join-Path $PSScriptRoot 'PySlate.ico'))
# Programmatic rasterization of PySlate's own web/icon.svg geometry.
if ($PSVersionTable.PSEdition -eq 'Core') {
  & (Join-Path $env:WINDIR 'System32\WindowsPowerShell\v1.0\powershell.exe') -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath -Destination $Destination
  if ($LASTEXITCODE -ne 0) { throw 'Icon generation failed' }
  return
}
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Drawing.Imaging;
using System.IO;
public static class PySlateIcon {
  static GraphicsPath Rounded(float x,float y,float w,float h,float r) {
    var p=new GraphicsPath();p.AddArc(x,y,r*2,r*2,180,90);p.AddArc(x+w-r*2,y,r*2,r*2,270,90);p.AddArc(x+w-r*2,y+h-r*2,r*2,r*2,0,90);p.AddArc(x,y+h-r*2,r*2,r*2,90,90);p.CloseFigure();return p;
  }
  public static void Write(string destination) {
    using(var bitmap=new Bitmap(256,256,PixelFormat.Format32bppArgb))
    using(var g=Graphics.FromImage(bitmap)) {
      g.Clear(Color.Transparent);g.SmoothingMode=SmoothingMode.AntiAlias;g.ScaleTransform(2,2);
      using(var background=Rounded(0,0,128,128,30)) using(var brush=new SolidBrush(ColorTranslator.FromHtml("#164c40"))) g.FillPath(brush,background);
      using(var p=new GraphicsPath(FillMode.Alternate)) {
        p.AddLine(37,92,37,35);p.AddLine(37,35,66,35);p.AddBezier(66,35,93,35,93,70,66,70);p.AddLine(66,70,50,70);p.AddLine(50,70,50,92);p.CloseFigure();
        p.StartFigure();p.AddLine(50,58,65,58);p.AddBezier(65,58,75,58,75,47,65,47);p.AddLine(65,47,50,47);p.CloseFigure();
        using(var brush=new SolidBrush(ColorTranslator.FromHtml("#e5f3df"))) g.FillPath(brush,p);
      }
      using(var underscore=Rounded(72,80,24,12,3)) using(var brush=new SolidBrush(ColorTranslator.FromHtml("#e8b66e"))) g.FillPath(brush,underscore);
      using(var pixels=new MemoryStream()) {
        bitmap.Save(pixels,ImageFormat.Png);byte[] data=pixels.ToArray();
        using(var output=new BinaryWriter(File.Create(destination))) {output.Write((ushort)0);output.Write((ushort)1);output.Write((ushort)1);output.Write((byte)0);output.Write((byte)0);output.Write((byte)0);output.Write((byte)0);output.Write((ushort)1);output.Write((ushort)32);output.Write(data.Length);output.Write(22);output.Write(data);}
      }
    }
  }
}
'@
[PySlateIcon]::Write([IO.Path]::GetFullPath($Destination))
