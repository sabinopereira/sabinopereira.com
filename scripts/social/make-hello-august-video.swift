import AppKit
import AVFoundation
import CoreImage
import CoreVideo

let arguments = CommandLine.arguments
guard arguments.count == 3 else {
    fputs("Usage: make-hello-august-video.swift <input-image> <output-video>\n", stderr)
    exit(2)
}

let inputURL = URL(fileURLWithPath: arguments[1])
let outputURL = URL(fileURLWithPath: arguments[2])
let width = 1080
let height = 1920
let fps: Int32 = 30
let durationSeconds = 9
let frameCount = Int(fps) * durationSeconds
let canvas = CGRect(x: 0, y: 0, width: width, height: height)

guard
    let source = NSImage(contentsOf: inputURL),
    let cgImage = source.cgImage(forProposedRect: nil, context: nil, hints: nil)
else {
    fputs("Could not load source image.\n", stderr)
    exit(3)
}

try? FileManager.default.removeItem(at: outputURL)

let writer = try AVAssetWriter(outputURL: outputURL, fileType: .mp4)
let settings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 8_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
    ]
]
let writerInput = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
writerInput.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: writerInput,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height
    ]
)

guard writer.canAdd(writerInput) else {
    fputs("Could not configure video writer.\n", stderr)
    exit(4)
}
writer.add(writerInput)
writer.startWriting()
writer.startSession(atSourceTime: .zero)

let context = CIContext(options: [.useSoftwareRenderer: false])
let sourceImage = CIImage(cgImage: cgImage)
let sourceExtent = sourceImage.extent
let colorSpace = CGColorSpaceCreateDeviceRGB()

func centeredTransform(for image: CIImage, scale: CGFloat) -> CIImage {
    let scaledWidth = image.extent.width * scale
    let scaledHeight = image.extent.height * scale
    let x = (CGFloat(width) - scaledWidth) / 2
    let y = (CGFloat(height) - scaledHeight) / 2
    return image.transformed(by: CGAffineTransform(scaleX: scale, y: scale))
        .transformed(by: CGAffineTransform(translationX: x, y: y))
}

for frame in 0..<frameCount {
    while !writerInput.isReadyForMoreMediaData {
        Thread.sleep(forTimeInterval: 0.002)
    }

    let progress = CGFloat(frame) / CGFloat(max(frameCount - 1, 1))
    let eased = progress * progress * (3 - 2 * progress)

    let backgroundBase = max(CGFloat(width) / sourceExtent.width, CGFloat(height) / sourceExtent.height)
    let backgroundScale = backgroundBase * (1.08 + 0.04 * eased)
    var background = centeredTransform(for: sourceImage, scale: backgroundScale)
        .clampedToExtent()
        .applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: 34.0])
        .cropped(to: canvas)
        .applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 0.78, kCIInputBrightnessKey: -0.08])

    let overlay = CIImage(color: CIColor(red: 0.09, green: 0.055, blue: 0.025, alpha: 0.18)).cropped(to: canvas)
    background = overlay.composited(over: background)

    let foregroundBase = CGFloat(width) / sourceExtent.width
    let foregroundScale = foregroundBase * (1.0 + 0.035 * eased)
    var foreground = centeredTransform(for: sourceImage, scale: foregroundScale).cropped(to: canvas)

    let fadeIn = min(1.0, progress / 0.08)
    let fadeOut = min(1.0, (1.0 - progress) / 0.08)
    let alpha = min(fadeIn, fadeOut)
    foreground = foreground.applyingFilter("CIColorMatrix", parameters: [
        "inputAVector": CIVector(x: 0, y: 0, z: 0, w: alpha)
    ])

    let composed = foreground.composited(over: background).cropped(to: canvas)
    var pixelBuffer: CVPixelBuffer?
    guard
        let pool = adaptor.pixelBufferPool,
        CVPixelBufferPoolCreatePixelBuffer(nil, pool, &pixelBuffer) == kCVReturnSuccess,
        let buffer = pixelBuffer
    else {
        fputs("Could not allocate video frame.\n", stderr)
        writer.cancelWriting()
        exit(5)
    }

    context.render(composed, to: buffer, bounds: canvas, colorSpace: colorSpace)
    let presentationTime = CMTime(value: CMTimeValue(frame), timescale: fps)
    adaptor.append(buffer, withPresentationTime: presentationTime)
}

writerInput.markAsFinished()
let completion = DispatchSemaphore(value: 0)
writer.finishWriting {
    completion.signal()
}
completion.wait()

if writer.status == .completed {
    print(outputURL.path)
} else {
    fputs("Video export failed: \(writer.error?.localizedDescription ?? "unknown error")\n", stderr)
    exit(6)
}
