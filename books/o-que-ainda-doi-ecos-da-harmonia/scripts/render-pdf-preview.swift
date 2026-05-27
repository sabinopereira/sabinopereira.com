import AppKit
import PDFKit

let args = CommandLine.arguments
guard args.count >= 3 else {
    fputs("Usage: render-pdf-preview.swift input.pdf output-dir [page...]\n", stderr)
    exit(2)
}

let pdfURL = URL(fileURLWithPath: args[1])
let outputDir = URL(fileURLWithPath: args[2], isDirectory: true)
let requestedPages = args.dropFirst(3).compactMap { Int($0) }

guard let document = PDFDocument(url: pdfURL) else {
    fputs("Could not open PDF\n", stderr)
    exit(1)
}

try FileManager.default.createDirectory(at: outputDir, withIntermediateDirectories: true)
print("pages=\(document.pageCount)")

let pages = requestedPages.isEmpty ? [0] : requestedPages
for index in pages where index >= 0 && index < document.pageCount {
    guard let page = document.page(at: index) else { continue }
    let image = page.thumbnail(of: CGSize(width: 900, height: 1350), for: .mediaBox)
    guard let tiff = image.tiffRepresentation,
          let rep = NSBitmapImageRep(data: tiff),
          let png = rep.representation(using: .png, properties: [:]) else {
        continue
    }

    let output = outputDir.appendingPathComponent(String(format: "page-%03d.png", index + 1))
    try png.write(to: output)
    print(output.path)
}
