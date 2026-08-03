import AppKit
import AVFoundation
import CoreImage
import CoreVideo
import Foundation

// Structs para decodificar a configuração JSON
struct SceneConfig: Decodable {
    let start: Double
    let end: Double
    let text: String
    let fontName: String?
    let fontSize: Double?
    let tracking: Double?
    let lineSpacing: Double?
}

struct ReelConfig: Decodable {
    let backgroundImage: String
    let audioFile: String
    let outputFile: String
    let duration: Double
    let brandName: String?
    let brandSubtitle: String?
    let scenes: [SceneConfig]
}

// 1. Validar Argumentos
let arguments = CommandLine.arguments
guard arguments.count == 2 else {
    fputs("Usage: swift make-aesthetic-reel.swift <config-json-path>\n", stderr)
    exit(1)
}

let configURL = URL(fileURLWithPath: arguments[1])
guard let data = try? Data(contentsOf: configURL) else {
    fputs("Error: Could not read configuration file at \(arguments[1])\n", stderr)
    exit(1)
}

// 2. Descodificar JSON
let decoder = JSONDecoder()
guard let config = try? decoder.decode(ReelConfig.self, from: data) else {
    fputs("Error: Failed to parse configuration JSON.\n", stderr)
    exit(1)
}

let width = 1080
let height = 1920
let fps: Int32 = 30
let durationSeconds = config.duration
let frameCount = Int(durationSeconds * Double(fps))
let canvas = CGRect(x: 0, y: 0, width: width, height: height)

let imageURL = URL(fileURLWithPath: config.backgroundImage)
let audioURL = URL(fileURLWithPath: config.audioFile)
let outputURL = URL(fileURLWithPath: config.outputFile)
let silentURL = outputURL.deletingLastPathComponent().appendingPathComponent("temp-silent-reel.mp4")

// 3. Carregar Imagem de Fundo
guard
    let nsImage = NSImage(contentsOf: imageURL),
    let sourceCG = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil)
else {
    fputs("Error: Could not load background image at \(config.backgroundImage)\n", stderr)
    exit(1)
}

// 4. Funções para Gerar Camadas de Texto de forma Robusta (Retina/Non-Retina)
func textLayer(_ text: String, fontName: String, fontSize: CGFloat, tracking: CGFloat, lineSpacing: CGFloat, width layerWidth: CGFloat, height layerHeight: CGFloat) -> CIImage {
    let image = NSImage(size: NSSize(width: layerWidth, height: layerHeight))
    image.lockFocusFlipped(true)
    NSColor.clear.setFill()
    NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight).fill()

    let style = NSMutableParagraphStyle()
    style.alignment = .center
    style.lineSpacing = lineSpacing
    
    let font = NSFont(name: fontName, size: fontSize) ?? NSFont.systemFont(ofSize: fontSize, weight: .medium)
    
    let shadow = NSShadow()
    shadow.shadowColor = NSColor.black.withAlphaComponent(0.55)
    shadow.shadowBlurRadius = 16
    shadow.shadowOffset = NSSize(width: 0, height: -3)
    
    let attributes: [NSAttributedString.Key: Any] = [
        .font: font,
        .foregroundColor: NSColor(calibratedRed: 0.97, green: 0.91, blue: 0.79, alpha: 1),
        .paragraphStyle: style,
        .kern: tracking,
        .shadow: shadow
    ]
    let attributed = NSAttributedString(string: text, attributes: attributes)
    let box = NSRect(x: 0, y: 0, width: layerWidth, height: layerHeight)
    attributed.draw(with: box, options: [.usesLineFragmentOrigin, .usesFontLeading])
    image.unlockFocus()

    guard let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
        fatalError("Could not render text layer")
    }
    
    // Normalizar escala para suportar ecrãs Retina e normais
    let scaleX = layerWidth / CGFloat(cg.width)
    let scaleY = layerHeight / CGFloat(cg.height)
    
    return CIImage(cgImage: cg).transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))
}

// 5. Preparar Camadas de Texto das Cenas
var sceneLayers: [CIImage] = []
for scene in config.scenes {
    let font = scene.fontName ?? "Didot"
    let size = CGFloat(scene.fontSize ?? 62)
    let kern = CGFloat(scene.tracking ?? 2.2)
    let spacing = CGFloat(scene.lineSpacing ?? 15)
    
    let layer = textLayer(scene.text, fontName: font, fontSize: size, tracking: kern, lineSpacing: spacing, width: 870, height: 520)
    sceneLayers.append(layer)
}

// 6. Preparar Camada da Marca (se definida)
var brandLayer: CIImage? = nil
if let brandName = config.brandName {
    let subtitle = config.brandSubtitle ?? "BOOKS • MUSIC • STORIES"
    let brandText = "\(brandName)\n\(subtitle)"
    brandLayer = textLayer(brandText, fontName: "Avenir Next Medium", fontSize: 22, tracking: 2.0, lineSpacing: 8, width: 860, height: 90)
}

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

// 7. Renderizar Vídeo Silencioso Temporário
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

print("Starting video frames generation...")

for frame in 0..<frameCount {
    while !writerInput.isReadyForMoreMediaData {
        Thread.sleep(forTimeInterval: 0.002)
    }
    
    let time = Double(frame) / Double(fps)
    let progress = CGFloat(time / durationSeconds)
    
    // Ken Burns Effect (Zoom suave e movimento subtil)
    let fillScale = max(CGFloat(width) / sourceExtent.width, CGFloat(height) / sourceExtent.height)
    let bgScale = fillScale * (1.05 + progress * 0.035)
    
    // Fundo desfoquado + escurecido
    var background = centered(source, scale: bgScale, xOffset: -100 + (progress * 20))
        .clampedToExtent()
        .applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: 15.0])
        .cropped(to: canvas)
        .applyingFilter("CIColorControls", parameters: [kCIInputSaturationKey: 0.82, kCIInputBrightnessKey: -0.15])
        
    let veil = CIImage(color: CIColor(red: 0.08, green: 0.045, blue: 0.025, alpha: 0.45)).cropped(to: canvas)
    background = veil.composited(over: background)
    
    var composed = background
    
    // Adicionar Marca se definida
    if let brand = brandLayer {
        // Centrar 860px em 1080px -> offset = (1080 - 860) / 2 = 110
        let positionedBrand = brand.transformed(by: CGAffineTransform(translationX: 110, y: 145))
        composed = positionedBrand.composited(over: composed)
    }
    
    // Adicionar Texto das Cenas
    for (index, scene) in config.scenes.enumerated() where time >= scene.start && time <= scene.end {
        let local = time - scene.start
        let remaining = scene.end - time
        let opacity = CGFloat(min(1.0, min(local / 0.42, remaining / 0.42)))
        
        // Efeito subtil de elevação (Rise transition)
        let rise = CGFloat(max(0, 1 - min(1, local / 0.7))) * -24
        
        // Centrar 870px em 1080px -> offset = (1080 - 870) / 2 = 105
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
        fputs("Error: Could not allocate pixel buffer.\n", stderr)
        exit(1)
    }
    
    context.render(composed.cropped(to: canvas), to: buffer, bounds: canvas, colorSpace: colorSpace)
    adaptor.append(buffer, withPresentationTime: CMTime(value: CMTimeValue(frame), timescale: fps))
}

writerInput.markAsFinished()
let writingDone = DispatchSemaphore(value: 0)
writer.finishWriting { writingDone.signal() }
writingDone.wait()

guard writer.status == .completed else {
    fputs("Error: Silent video export failed.\n", stderr)
    exit(1)
}

print("Silent video generated successfully. Merging audio...")

// 8. Mesclar Áudio e Exportar Vídeo Final
let videoAsset = AVURLAsset(url: silentURL)
let audioAsset = AVURLAsset(url: audioURL)
let composition = AVMutableComposition()

guard
    let sourceVideo = videoAsset.tracks(withMediaType: .video).first,
    let sourceAudio = audioAsset.tracks(withMediaType: .audio).first,
    let videoTrack = composition.addMutableTrack(withMediaType: .video, preferredTrackID: kCMPersistentTrackID_Invalid),
    let audioTrack = composition.addMutableTrack(withMediaType: .audio, preferredTrackID: kCMPersistentTrackID_Invalid)
else {
    fputs("Error: Could not extract tracks from assets.\n", stderr)
    try? FileManager.default.removeItem(at: silentURL)
    exit(1)
}

let totalDuration = CMTime(seconds: durationSeconds, preferredTimescale: 600)
try videoTrack.insertTimeRange(CMTimeRange(start: .zero, duration: totalDuration), of: sourceVideo, at: .zero)

let availableAudio = min(audioAsset.duration.seconds, durationSeconds)
try audioTrack.insertTimeRange(CMTimeRange(start: .zero, duration: CMTime(seconds: availableAudio, preferredTimescale: 600)), of: sourceAudio, at: .zero)

// Fade-in e Fade-out no áudio
let audioParameters = AVMutableAudioMixInputParameters(track: audioTrack)
audioParameters.setVolumeRamp(fromStartVolume: 0, toEndVolume: 0.85, timeRange: CMTimeRange(start: .zero, duration: CMTime(seconds: 0.8, preferredTimescale: 600)))
audioParameters.setVolumeRamp(fromStartVolume: 0.85, toEndVolume: 0, timeRange: CMTimeRange(start: CMTime(seconds: durationSeconds - 1.2, preferredTimescale: 600), duration: CMTime(seconds: 1.2, preferredTimescale: 600)))
let audioMix = AVMutableAudioMix()
audioMix.inputParameters = [audioParameters]

guard let exporter = AVAssetExportSession(asset: composition, presetName: AVAssetExportPresetHighestQuality) else {
    fputs("Error: Could not initialize AVAssetExportSession.\n", stderr)
    try? FileManager.default.removeItem(at: silentURL)
    exit(1)
}

exporter.outputURL = outputURL
exporter.outputFileType = .mp4
exporter.audioMix = audioMix

let exportDone = DispatchSemaphore(value: 0)
exporter.exportAsynchronously { exportDone.signal() }
exportDone.wait()

// Limpar temporário silencioso
try? FileManager.default.removeItem(at: silentURL)

guard exporter.status == .completed else {
    fputs("Error: Final render export failed: \(exporter.error?.localizedDescription ?? "unknown error")\n", stderr)
    exit(1)
}

print("SUCCESS: Cinematic Reel generated at: \(outputURL.path)")
