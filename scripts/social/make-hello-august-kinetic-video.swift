import AppKit
import AVFoundation
import CoreImage
import CoreVideo

let args = CommandLine.arguments
guard args.count == 4 else {
    fputs("Usage: make-hello-august-kinetic-video.swift <image> <audio> <output>\n", stderr)
    exit(2)
}

let imageURL = URL(fileURLWithPath: args[1])
let audioURL = URL(fileURLWithPath: args[2])
let outputURL = URL(fileURLWithPath: args[3])
let silentURL = outputURL.deletingLastPathComponent().appendingPathComponent("hello-august-kinetic-silent.mp4")
let width = 1080
let height = 1920
let fps: Int32 = 30
let durationSeconds: Double = 16
let frameCount = Int(durationSeconds * Double(fps))
let canvas = CGRect(x: 0, y: 0, width: width, height: height)

struct Scene {
    let start: Double
    let end: Double
    let text: String
    let title: Bool
}

let scenes = [
    Scene(start: 0.0, end: 2.6, text: "HELLO,\nAUGUST.", title: true),
    Scene(start: 2.4, end: 5.1, text: "A NEW MONTH.\nA BLANK PAGE.", title: false),
    Scene(start: 4.9, end: 8.1, text: "ANOTHER CHANCE TO CREATE\nSOMETHING WORTH REMEMBERING.", title: false),
    Scene(start: 7.9, end: 11.2, text: "CHOOSE CURIOSITY OVER FEAR.\nPROGRESS OVER PERFECTION.", title: false),
    Scene(start: 11.0, end: 14.1, text: "PEACEFUL MORNINGS.\nBOLD IDEAS.\nUNEXPECTED ADVENTURES.", title: false),
    Scene(start: 13.9, end: 16.0, text: "LET’S MAKE IT COUNT.", title: true)
]

guard
    let nsImage = NSImage(contentsOf: imageURL),
    let sourceCG = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil)
else {
    fputs("Could not load source image.\n", stderr)
    exit(3)
}

func textLayer(_ text: String, title: Bool) -> CIImage {
    let layerWidth: CGFloat = 870
    let layerHeight: CGFloat = 520
    let image = NSImage(size: NSSize(width: layerWidth, height: layerHeight))
    image.lockFocusFlipped(true)
    NSColor.clear.setFill()
    NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight).fill()

    let style = NSMutableParagraphStyle()
    style.alignment = .center
    style.lineSpacing = title ? 4 : 15
    let font = title
        ? (NSFont(name: "Didot", size: 112) ?? NSFont.systemFont(ofSize: 112, weight: .medium))
        : (NSFont(name: "Avenir Next Demi Bold", size: 62) ?? NSFont.systemFont(ofSize: 62, weight: .semibold))
    let shadow = NSShadow()
    shadow.shadowColor = NSColor.black.withAlphaComponent(0.55)
    shadow.shadowBlurRadius = 16
    shadow.shadowOffset = NSSize(width: 0, height: -3)
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor(calibratedRed: 0.97, green: 0.91, blue: 0.79, alpha: 1),
        .paragraphStyle: style,
        .kern: title ? 4.0 : 2.2,
        .shadow: shadow
    ]
    let attributed = NSAttributedString(string: text, attributes: attributes)
    let box = NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight)
    attributed.draw(with: box, options: [.usesLineFragmentOrigin, .usesFontLeading])
    image.unlockFocus()

    guard let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fatalError("Could not render text")
    }
    return CIImage(cgImage: cg)
}

func brandLayer() -> CIImage {
    let layerWidth: CGFloat = 860
    let layerHeight: CGFloat = 90
    let image = NSImage(size: NSSize(width: layerWidth, height: layerHeight))
    image.lockFocusFlipped(true)
    NSColor.clear.setFill()
    NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight).fill()
    let style = NSMutableParagraphStyle()
    style.alignment = .center
    style.lineSpacing = 8
    let brand = NSAttributedString(string: "REIRA BIN\nBOOKS • MUSIC • STORIES • EXPERIENCES.", attributes: [
        .font: NSFont(name: "Avenir Next Medium", size: 22) ?? NSFont.systemFont(ofSize: 22),
        .foregroundColor: NSColor.white.withAlphaComponent(0.78),
        .paragraphStyle: style,
        .kern: 2.0
    ])
    brand.draw(with: NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight), options: [.usesLineFragmentOrigin])
    image.unlockFocus()
    guard let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { fatalError("Could not render brand") }
    return CIImage(cgImage: cg)
}

let retinaToPixels = CGAffineTransform(scaleX: 0.5, y: 0.5)
let sceneLayers = scenes.map { textLayer($0.text, title: $0.title).transformed(by: retinaToPixels) }
let brand = brandLayer()
    .transformed(by: retinaToPixels)
    .transformed(by: CGAffineTransform(translationX: 110, y: 145))
let source = CIImage(cgImage: sourceCG)
let sourceExtent = source.extent
let context = CIContext(options: [.useSoftwareRenderer: false])
let colorSpace = CGColorSpaceCreateDeviceRGB()

func centered(_ image: CIImage, scale: CGFloat, xOffset: CGFloat = 0) -> CIImage {
    let scaledWidth = image.extent.width * scale
    let scaledHeight = image.extent.height * scale
    let x = (CGFloat(width) - scaledWidth) / 2 + xOffset
    let y = (CGFloat(height) - scaledHeight) / 2
    return image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        .transformed(by: CGAffineTransform(translationX: x, y: y))
}

try? FileManager.default.removeItem(at: silentURL)
try? FileManager.default.removeItem(at: outputURL)
let writer = try AVAssetWriter(outputURL: silentURL, fileType: .mp4)
let writerInput = AVAssetWriterInput(mediaType: .video, outputSettings: [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [AVVideoAverageBitRateKey: 8_000_000]
])
writerInput.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: writerInput, sourcePixelBufferAttributes: [
    kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
    kCVPixelBufferWidthKey as String: width,
    kCVPixelBufferHeightKey as String: height
])
writer.add(writerInput)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

for frame in 0..<frameCount {
    while !writerInput.isReadyForMoreMediaData { Thread.sleep(forTimeInterval: 0.002) }
    let time = Double(frame) / Double(fps)
    let progress = CGFloat(time / durationSeconds)
    let fillScale = max(CGFloat(width) / sourceExtent.width, CGFloat(height) / sourceExtent.height)
    let bgScale = fillScale * (1.05 + progress * 0.035)
    var background = centered(source, scale: bgScale, xOffset: -115)
        .clampedToExtent()
        .applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: 14.0])
        .cropped(to: canvas)
        .applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 0.88, kCIInputBrightnessKey: -0.12])
    let veil = CIImage(color: CIColor(red: 0.08, green: 0.045, blue: 0.025, alpha: 0.42)).cropped(to: canvas)
    background = veil.composited(over: background)

    var composed = brand.composited(over: background)
    for (index, scene) in scenes.enumerated() where time >= scene.start && time <= scene.end {
        let local = time - scene.start
        let remaining = scene.end - time
        let opacity = CGFloat(min(1.0, min(local / 0.42, remaining / 0.42)))
        let rise = CGFloat(max(0, 1 - min(1, local / 0.7))) * -24
        let layer = sceneLayers[index]
            .transformed(by: CGAffineTransform(translationX: 105, y: 700 + rise))
            .applyingFilter("CIColorMatrix", parameters: ["inputAVector": CIVector(x: 0, y: 0, z: 0, w: opacity)])
        composed = layer.composited(over: composed)
    }

    var pixelBuffer: CVPixelBuffer?
    guard let pool = adaptor.pixelBufferPool,
          CVPixelBufferPoolCreatePixelBuffer(nil, pool, &pixelBuffer) == kCVReturnSuccess,
          let buffer = pixelBuffer else {
        writer.cancelWriting()
        exit(4)
    }
    context.render(composed.cropped(to: canvas), to: buffer, bounds: canvas, colorSpace: colorSpace)
    adaptor.append(buffer, withPresentationTime: CMTime(value: CMTimeValue(frame), timescale: fps))
}

writerInput.markAsFinished()
let writingDone = DispatchSemaphore(value: 0)
writer.finishWriting { writingDone.signal() }
writingDone.wait()
guard writer.status == .completed else {
    fputs("Silent video export failed.\n", stderr)
    exit(5)
}

let videoAsset = AVURLAsset(url: silentURL)
let audioAsset = AVURLAsset(url: audioURL)
let composition = AVMutableComposition()
guard
    let sourceVideo = videoAsset.tracks(withMediaType: .video).first,
    let sourceAudio = audioAsset.tracks(withMediaType: .audio).first,
    let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
    let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)
else {
    fputs("Could not load video or audio tracks.\n", stderr)
    exit(6)
}

let totalDuration = CMTime(seconds: durationSeconds, preferredTimescale: 600)
try videoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: totalDuration), of: sourceVideo, at: .zero)
let availableAudio = min(audioAsset.duration.seconds, durationSeconds)
try audioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: CMTime(seconds: availableAudio, preferredTimescale: 600)), of: sourceAudio, at: .zero)

let audioParameters = AVMutableAudioMixInputParameters(track: audioTrack)
audioParameters.setVolumeRamp(fromStartVolume: 0, toEndVolume: 0.82, timeRange: CMTimeRange(start: .zero, duration: CMTime(seconds: 0.7, preferredTimescale: 600)))
audioParameters.setVolumeRamp(fromStartVolume: 0.82, toEndVolume: 0, timeRange: CMTimeRange(start: CMTime(seconds: 14.8, preferredTimescale: 600), duration: CMTime(seconds: 1.2, preferredTimescale: 600)))
let audioMix = AVMutableAudioMix()
audioMix.inputParameters = [audioParameters]

guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
    fputs("Could not create final exporter.\n", stderr)
    exit(7)
}
exporter.outputURL = outputURL
exporter.outputFileType = .mp4
exporter.audioMix = audioMix
let exportDone = DispatchSemaphore(value: 0)
exporter.exportAsynchronously { exportDone.signal() }
exportDone.wait()
try? FileManager.default.removeItem(at: silentURL)

guard exporter.status == .completed else {
    fputs("Final export failed: \(exporter.error?.localizedDescription ?? "unknown error")\n", stderr)
    exit(8)
}
print(outputURL.path)
