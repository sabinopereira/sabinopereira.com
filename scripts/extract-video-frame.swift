import Foundation
import AVFoundation
import AppKit

let videoURL = URL(fileURLWithPath: CommandLine.arguments[1])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[2])
let second = Double(CommandLine.arguments[3]) ?? 1.0
let generator = AVAssetImageGenerator(asset: AVURLAsset(url: videoURL))
generator.appliesPreferredTrackTransform = true
let image = try generator.copyCGImage(at: CMTime(seconds: second, preferredTimescale: 600), actualTime: nil)
let bitmap = NSBitmapImageRep(cgImage: image)
try bitmap.representation(using: .png, properties: [:])!.write(to: outputURL)
