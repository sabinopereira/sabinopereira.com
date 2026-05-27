import Foundation
import PDFKit

let args = CommandLine.arguments
guard args.count >= 2 else {
    fputs("Usage: check-pdf-text.swift input.pdf\n", stderr)
    exit(2)
}

let pdfURL = URL(fileURLWithPath: args[1])
guard let document = PDFDocument(url: pdfURL) else {
    fputs("Could not open PDF\n", stderr)
    exit(1)
}

let text = document.string ?? ""
print("pages=\(document.pageCount)")

let needles = [
    "Ficheiro 2",
    "Jonas e o Grande Vazio",
    "A Harmonia chamou-lhe falha",
    "PART E",
    "Texto integral",
    "undefined",
    "truncated"
]

for needle in needles {
    print("\(needle): \(text.contains(needle))")
}
