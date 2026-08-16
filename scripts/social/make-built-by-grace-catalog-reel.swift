import AppKit
import AVFoundation
import CoreImage
import CoreVideo
import Foundation

let args = CommandLine.arguments
guard args.count >= 5 else {
    fputs("Usage: swift make-built-by-grace-catalog-reel.swift <output.mp4> <audio.wav> <image1> <image2> [image3 ...]\n", stderr)
    exit(1)
}

let outputURL = URL(fileURLWithPath: args[1])
let audioURL = URL(fileURLWithPath: args[2])
let imageURLs = args[3...].map { URL(fileURLWithPath: $0) }
let width = 1080
let height = 1920
let fps: Int32 = 30
let sceneDuration = 3.2
let duration = sceneDuration * Double(imageURLs.count)
let canvas = CGRect(x: 0, y: 0, width: width, height: height)
let context = CIContext()
let colourSpace = CGColorSpaceCreateDeviceRGB()

let images: [CIImage] = imageURLs.compactMap { url in
    guard let image = NSImage(contentsOf: url),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { return nil }
    return CIImage(cgImage: cg)
}
guard images.count == imageURLs.count else {
    fputs("Could not load every cover image\n", stderr)
    exit(1)
}

func placed(_ image: CIImage, fill: Bool, zoom: CGFloat = 1) -> CIImage {
    let sx = CGFloat(width) / image.extent.width
    let sy = CGFloat(height) / image.extent.height
    let scale = (fill ? max(sx, sy) : min(sx, sy)) * zoom
    let scaled = image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
    let x = (CGFloat(width) - scaled.extent.width) / 2
    let y = (CGFloat(height) - scaled.extent.height) / 2
    return scaled.transformed(by: CGAffineTransform(translationX: x, y: y))
}

func frame(for image: CIImage, progress: CGFloat) -> CIImage {
    let backdrop = placed(image, fill: true, zoom: 1.04 + progress * 0.02)
        .clampedToExtent()
        .applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: 30])
        .cropped(to: canvas)
        .applyingFilter("CIColorControls", parameters: [
            kCIInputSaturationKey: 0.82,
            kCIInputBrightnessKey: -0.14,
            kCIInputContrastKey: 1.04
        ])
    let veil = CIImage(color: CIColor(red: 0.025, green: 0.020, blue: 0.016, alpha: 0.34)).cropped(to: canvas)
    let foreground = placed(image, fill: false, zoom: 0.965 + progress * 0.018)
    return foreground.composited(over: veil.composited(over: backdrop)).cropped(to: canvas)
}

let tempURL = outputURL.deletingLastPathComponent().appendingPathComponent("built-by-grace-catalog-silent.mp4")
try? FileManager.default.removeItem(at: tempURL)
try? FileManager.default.removeItem(at: outputURL)

let writer = try AVAssetWriter(outputURL: tempURL, fileType: .mp4)
let input = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 7_000_000]
])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: input, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
])
writer.add(input)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

let frameTotal = Int(duration * Double(fps))
for frameIndex in 0..<frameTotal {
    while !input.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
    let seconds = Double(frameIndex) / Double(fps)
    let scene = min(images.count - 1, Int(seconds / sceneDuration))
    let local = (seconds - Double(scene) * sceneDuration) / sceneDuration
    var rendered = frame(for: images[scene], progress: CGFloat(local))
    if scene + 1 < images.count && local > 0.82 {
        let mix = CGFloat((local - 0.82) / 0.18)
        let next = frame(for: images[scene + 1], progress: 0)
            .applyingFilter("CIColorMatrix", parameters: ["inputAVector": CIVector(x: 0, y: 0, z: 0, w: mix)])
        rendered = next.composited(over: rendered)
    }
    var buffer: CVPixelBuffer?
    guard let pool = adaptor.pixelBufferPool,
          CVPixelBufferPoolCreatePixelBuffer(nil, pool, &buffer) == kCVReturnSuccess,
          let pixelBuffer = buffer else { fatalError("Pixel buffer allocation failed") }
    context.render(rendered, to: pixelBuffer, bounds: canvas, colorSpace: colourSpace)
    adaptor.append(pixelBuffer, withPresentationTime: CMTime(value: CMTimeValue(frameIndex), timescale: fps))
}
input.markAsFinished()
let done = DispatchSemaphore(value: 0)
writer.finishWriting { done.signal() }
done.wait()
guard writer.status == .completed else { fatalError("Video render failed: \(writer.error?.localizedDescription ?? "unknown")") }

let videoAsset = AVURLAsset(url: tempURL)
let audioAsset = AVURLAsset(url: audioURL)
let composition = AVMutableComposition()
guard let sourceVideo = videoAsset.tracks(withMediaType: .video).first,
      let sourceAudio = audioAsset.tracks(withMediaType: .audio).first,
      let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
      let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid) else {
    fatalError("Could not prepare media tracks")
}
let total = CMTime(seconds: duration, preferredTimescale: 600)
try videoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: total), of: sourceVideo, at: .zero)
try audioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: total), of: sourceAudio, at: .zero)
let audioMix = AVMutableAudioMix()
let parameters = AVMutableAudioMixInputParameters(track: audioTrack)
parameters.setVolume(0.84, at: .zero)
parameters.setVolumeRamp(fromStartVolume: 0.84, toEndVolume: 0, timeRange: CMTimeRange(start: CMTime(seconds: duration - 1.2, preferredTimescale: 600), duration: CMTime(seconds: 1.2, preferredTimescale: 600)))
audioMix.inputParameters = [parameters]
guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else { fatalError("Exporter unavailable") }
exporter.outputURL = outputURL
exporter.outputFileType = .mp4
exporter.audioMix = audioMix
let exported = DispatchSemaphore(value: 0)
exporter.exportAsynchronously { exported.signal() }
exported.wait()
try? FileManager.default.removeItem(at: tempURL)
guard exporter.status == .completed else { fatalError("Export failed: \(exporter.error?.localizedDescription ?? "unknown")") }
print(outputURL.path)
