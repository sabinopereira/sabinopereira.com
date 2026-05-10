import AVFoundation
import AppKit
import CoreVideo
import Foundation

struct StaticVideoError: Error, CustomStringConvertible {
    let description: String
}

func fail(_ message: String) throws -> Never {
    throw StaticVideoError(description: message)
}

guard CommandLine.arguments.count == 4 else {
    try fail("Usage: swift make_static_audio_video.swift <image.png> <audio.mp3> <output.mp4>")
}

let imageURL = URL(fileURLWithPath: CommandLine.arguments[1])
let audioURL = URL(fileURLWithPath: CommandLine.arguments[2])
let outputURL = URL(fileURLWithPath: CommandLine.arguments[3])
let tempVideoURL = outputURL.deletingLastPathComponent().appendingPathComponent("__static_video_temp.mov")

try? FileManager.default.removeItem(at: outputURL)
try? FileManager.default.removeItem(at: tempVideoURL)

guard let image = NSImage(contentsOf: imageURL) else {
    try fail("Could not read image at \(imageURL.path)")
}

let audioAsset = AVURLAsset(url: audioURL)
let duration = try await audioAsset.load(.duration)
let totalSeconds = CMTimeGetSeconds(duration)
guard totalSeconds.isFinite, totalSeconds > 0 else {
    try fail("Could not read audio duration")
}

let width = 1920
let height = 1080
let fps: Int32 = 30
let frameCount = Int(ceil(totalSeconds * Double(fps)))

let writer = try AVAssetWriter(outputURL: tempVideoURL, fileType: .mov)
let videoSettings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.h264,
    AVVideoWidthKey: width,
    AVVideoHeightKey: height,
    AVVideoCompressionPropertiesKey: [
        AVVideoAverageBitRateKey: 1_200_000,
        AVVideoProfileLevelKey: AVVideoProfileLevelH264HighAutoLevel
    ]
]

let videoInput = AVAssetWriterInput(mediaType: .video, outputSettings: videoSettings)
videoInput.expectsMediaDataInRealTime = false

let adaptor = AVAssetWriterInputPixelBufferAdaptor(
    assetWriterInput: videoInput,
    sourcePixelBufferAttributes: [
        kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA,
        kCVPixelBufferWidthKey as String: width,
        kCVPixelBufferHeightKey as String: height
    ]
)

guard writer.canAdd(videoInput) else {
    try fail("Could not add video input")
}
writer.add(videoInput)

guard writer.startWriting() else {
    try fail(writer.error?.localizedDescription ?? "Could not start video writer")
}
writer.startSession(atSourceTime: .zero)

func makePixelBuffer(from image: NSImage) throws -> CVPixelBuffer {
    var pixelBuffer: CVPixelBuffer?
    let attrs = [
        kCVPixelBufferCGImageCompatibilityKey: true,
        kCVPixelBufferCGBitmapContextCompatibilityKey: true
    ] as CFDictionary

    let status = CVPixelBufferCreate(kCFAllocatorDefault, width, height, kCVPixelFormatType_32BGRA, attrs, &pixelBuffer)
    guard status == kCVReturnSuccess, let pixelBuffer else {
        try fail("Could not create pixel buffer")
    }

    CVPixelBufferLockBaseAddress(pixelBuffer, [])
    defer { CVPixelBufferUnlockBaseAddress(pixelBuffer, []) }

    guard let context = CGContext(
        data: CVPixelBufferGetBaseAddress(pixelBuffer),
        width: width,
        height: height,
        bitsPerComponent: 8,
        bytesPerRow: CVPixelBufferGetBytesPerRow(pixelBuffer),
        space: CGColorSpaceCreateDeviceRGB(),
        bitmapInfo: CGImageAlphaInfo.premultipliedFirst.rawValue | CGBitmapInfo.byteOrder32Little.rawValue
    ) else {
        try fail("Could not create bitmap context")
    }

    context.interpolationQuality = .high
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(cgContext: context, flipped: false)
    image.draw(in: CGRect(x: 0, y: 0, width: width, height: height))
    NSGraphicsContext.restoreGraphicsState()
    return pixelBuffer
}

let pixelBuffer = try makePixelBuffer(from: image)
let frameDuration = CMTime(value: 1, timescale: fps)

for frame in 0..<frameCount {
    while !videoInput.isReadyForMoreMediaData {
        Thread.sleep(forTimeInterval: 0.01)
    }
    let presentationTime = CMTimeMultiply(frameDuration, multiplier: Int32(frame))
    guard adaptor.append(pixelBuffer, withPresentationTime: presentationTime) else {
        try fail(writer.error?.localizedDescription ?? "Could not append video frame")
    }
}

videoInput.markAsFinished()
await writer.finishWriting()
if writer.status != .completed {
    try fail(writer.error?.localizedDescription ?? "Video writer did not complete")
}

let composition = AVMutableComposition()
let silentVideo = AVURLAsset(url: tempVideoURL)

guard
    let compositionVideo = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
    let sourceVideo = try await silentVideo.loadTracks(withMediaType: .video).first
else {
    try fail("Could not create video composition")
}

try compositionVideo.insertTimeRange(CMTimeRange(start: .zero, duration: duration), of: sourceVideo, at: .zero)

guard
    let compositionAudio = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid),
    let sourceAudio = try await audioAsset.loadTracks(withMediaType: .audio).first
else {
    try fail("Could not read audio track")
}

try compositionAudio.insertTimeRange(CMTimeRange(start: .zero, duration: duration), of: sourceAudio, at: .zero)

guard let export = AVAssetExportSession(asset: composition, presetName: AVAssetExportPreset1920x1080) else {
    try fail("Could not create export session")
}

export.outputURL = outputURL
export.outputFileType = .mp4
export.shouldOptimizeForNetworkUse = true

await export.export()

try? FileManager.default.removeItem(at: tempVideoURL)

if export.status != .completed {
    try fail(export.error?.localizedDescription ?? "Export did not complete")
}

print("Created \(outputURL.path)")
