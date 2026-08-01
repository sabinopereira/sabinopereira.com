import AppKit
import AVFoundation

guard CommandLine.arguments.count == 4,
      let seconds = Double(CommandLine.arguments[2]) else {
    fputs("Usage: extract-video-frame.swift <video> <seconds> <output.png>\n", stderr)
    exit(2)
}

let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[3])
let asset = AVURLAsset(url: videoURL)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true
generator.requestedTimeToleranceBefore = .zero
generator.requestedTimeToleranceAfter = .zero
let image = try generator.copyCGImage(at: CMTime(seconds: seconds, preferredTimescale: 600), actualTime: nil)
let bitmap = NSBitmapImageRep(cgImage: image)
guard let data = bitmap.representation(using: .png, properties: [:]) else { exit(3) }
try data.write(to: outputURL)
