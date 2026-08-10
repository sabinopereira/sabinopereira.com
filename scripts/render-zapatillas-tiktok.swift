import Foundation
import AVFoundation
import AppKit
import CoreVideo

let coverPath = "/Users/binopereira/Desktop/musicas soltas verao/Zapatillas bajo la mesa - capa v2.jpg"
let audioPath = "/Users/binopereira/Desktop/musicas soltas verao/Zapatillas bajo la mesa.wav"
let outputPath = "/Users/binopereira/Desktop/Site SabinoPereira.com/sabinopereira.com/social-media/zapatillas-bajo-la-mesa/zapatillas-tiktok-01.mp4"

let width = 1080
let height = 1920
let fps: Int32 = 30
let duration = 15.0
let audioStart = 50.0

guard let cover = NSImage(contentsOfFile: coverPath) else {
    fatalError("Could not load cover")
}

try FileManager.default.createDirectory(
    at: URL(fileURLWithPath: outputPath).deletingLastPathComponent(),
    withIntermediateDirectories: true
)
try? FileManager.default.removeItem(atPath: outputPath)

let writer = try AVAssetWriter(outputURL: URL(fileURLWithPath: outputPath), fileType: .mp4)
let videoSettings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 8_000_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
    ]
]
let videoInput = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
videoInput.expectsMediaDataInRealTime = false
let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: videoInput,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32ARGB,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height
    ]
)
guard writer.canAdd(videoInput) else { fatalError("Cannot add video input") }
writer.add(videoInput)

let composition = AVMutableComposition()
let sourceAsset = AVURLAsset(url: URL(fileURLWithPath: audioPath))
guard let sourceAudio = sourceAsset.tracks(withMediaType: .audio).first,
      let compositionAudio = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)
else { fatalError("Could not load audio") }
try compositionAudio.insertTimeRange(
    CMTimeRange(start: CMTime(seconds: audioStart, preferredTimescale: 600), duration: CMTime(seconds: duration, preferredTimescale: 600)),
    of: sourceAudio,
    at: .zero
)
let reader = try AVAssetReader(asset: composition)
let audioOutput = AVAssetReaderTrackOutput(track: compositionAudio, outputSettings: [
    AVFormatIDKey: kAudioFormatLinearPCM,
    AVLinearPCMBitDepthKey: 16,
    AVLinearPCMIsFloatKey: false,
    AVLinearPCMIsBigEndianKey: false,
    AVLinearPCMIsNonInterleaved: false
])
reader.add(audioOutput)
let audioInput = AVAssetWriterInput(mediaType: .audio, outputSettings: [
    AVFormatIDKey: kAudioFormatMPEG4AAC,
    AVSampleRateKey: 44_100,
    AVNumberOfChannelsKey: 2,
    AVEncoderBitRateKey: 192_000
])
audioInput.expectsMediaDataInRealTime = false
guard writer.canAdd(audioInput) else { fatalError("Cannot add audio input") }
writer.add(audioInput)

func drawCentered(_ text: String, y: CGFloat, size: CGFloat, color: NSColor, weight: NSFont.Weight = .bold, maxWidth: CGFloat = 920) {
    let paragraph = NSMutableParagraphStyle()
    paragraph.alignment = .center
    paragraph.lineSpacing = 4
    let attrs: [NSAttributedString.Key: Any] = [
        .font: NSFont.systemFont(ofSize: size, weight: weight),
        .foregroundColor: color,
        .paragraphStyle: paragraph,
        .strokeColor: NSColor.black.withAlphaComponent(0.75),
        .strokeWidth: -3.0
    ]
    let rect = NSRect(x: (CGFloat(width) - maxWidth) / 2, y: y, width: maxWidth, height: 240)
    text.draw(with: rect, options: [.usesLineFragmentOrigin, .usesFontLeading], attributes: attrs)
}

func makeFrame(second: Double) -> CVPixelBuffer {
    var buffer: CVPixelBuffer?
    CVPixelBufferPoolCreatePixelBuffer(nil, adaptor.pixelBufferPool!, &buffer)
    let pixelBuffer = buffer!
    CVPixelBufferLockBaseAddress(pixelBuffer, [])
    let context = CGContext(
        data: CVPixelBufferGetBaseAddress(pixelBuffer),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.noneSkipFirst.rawValue
    )!
    let graphics = NSGraphicsContext(cgContext: context, flipped: false)
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = graphics

    NSColor(calibratedWhite: 0.02, alpha: 1).setFill()
    NSRect(x: 0, y: 0, width: width, height: height).fill()

    let zoom = 1.0 + 0.035 * CGFloat(second / duration)
    let bgSize = CGFloat(height) * zoom
    let bgRect = NSRect(x: (CGFloat(width) - bgSize) / 2, y: (CGFloat(height) - bgSize) / 2, width: bgSize, height: bgSize)
    cover.draw(in: bgRect, from: .zero, operation: .sourceOver, fraction: 0.38)
    NSColor.black.withAlphaComponent(0.42).setFill()
    NSRect(x: 0, y: 0, width: width, height: height).fill()

    let cardSize = CGFloat(width) * 0.92 * zoom
    let cardY = 540 - (cardSize - CGFloat(width) * 0.92) / 2
    let cardRect = NSRect(x: (CGFloat(width) - cardSize) / 2, y: cardY, width: cardSize, height: cardSize)
    NSGraphicsContext.current?.cgContext.setShadow(offset: CGSize(width: 0, height: -15), blur: 35, color: NSColor.black.withAlphaComponent(0.8).cgColor)
    cover.draw(in: cardRect, from: .zero, operation: .sourceOver, fraction: 1)
    NSGraphicsContext.current?.cgContext.setShadow(offset: .zero, blur: 0, color: nil)

    if second < 3.4 {
        drawCentered("OYE TÚ,", y: 1575, size: 92, color: NSColor(calibratedRed: 1, green: 0.83, blue: 0.05, alpha: 1))
        drawCentered("NO ME DEJES SENTADO", y: 1455, size: 58, color: .white)
    } else if second < 6.9 {
        drawCentered("QUE LA PLAZA ENTERA", y: 1575, size: 58, color: .white)
        drawCentered("SE PUSO A BAILAR", y: 1455, size: 78, color: NSColor(calibratedRed: 1, green: 0.83, blue: 0.05, alpha: 1))
    } else if second < 10.5 {
        drawCentered("DAME UNA VUELTA,", y: 1575, size: 70, color: NSColor(calibratedRed: 1, green: 0.83, blue: 0.05, alpha: 1))
        drawCentered("QUÉDATE A MI LADO", y: 1455, size: 62, color: .white)
    } else if second < 14.1 {
        drawCentered("ESTA NOCHE", y: 1580, size: 64, color: .white)
        drawCentered("NO SE PUEDE DESPERDICIAR", y: 1450, size: 49, color: NSColor(calibratedRed: 1, green: 0.83, blue: 0.05, alpha: 1))
    } else {
        drawCentered("ZAPATILLAS BAJO LA MESA", y: 1555, size: 53, color: NSColor(calibratedRed: 1, green: 0.83, blue: 0.05, alpha: 1))
        drawCentered("REIRA BIN · OUT NOW", y: 1460, size: 36, color: .white, weight: .semibold)
    }

    NSGraphicsContext.restoreGraphicsState()
    CVPixelBufferUnlockBaseAddress(pixelBuffer, [])
    return pixelBuffer
}

writer.startWriting()
writer.startSession(atSourceTime: .zero)
reader.startReading()

let videoQueue = DispatchQueue(label: "video.queue")
let audioQueue = DispatchQueue(label: "audio.queue")
let group = DispatchGroup()

group.enter()
videoInput.requestMediaDataWhenReady(on: videoQueue) {
    var frame: Int64 = 0
    let totalFrames = Int64(duration * Double(fps))
    while videoInput.isReadyForMoreMediaData && frame < totalFrames {
        let second = Double(frame) / Double(fps)
        let buffer = makeFrame(second: second)
        adaptor.append(buffer, withPresentationTime: CMTime(value: frame, timescale: fps))
        frame += 1
    }
    if frame >= totalFrames {
        videoInput.markAsFinished()
        group.leave()
    }
}

group.enter()
audioInput.requestMediaDataWhenReady(on: audioQueue) {
    while audioInput.isReadyForMoreMediaData {
        if let sample = audioOutput.copyNextSampleBuffer() {
            audioInput.append(sample)
        } else {
            audioInput.markAsFinished()
            group.leave()
            break
        }
    }
}

group.wait()
let semaphore = DispatchSemaphore(value: 0)
writer.finishWriting { semaphore.signal() }
semaphore.wait()

if writer.status != .completed {
    fatalError("Render failed: \(writer.error?.localizedDescription ?? "unknown error")")
}
print(outputPath)
