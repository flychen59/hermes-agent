import Vision
import Foundation
import CoreImage
import AppKit

let args = CommandLine.arguments
guard args.count > 1 else { print("Usage: ocr <image_path>"); exit(1) }
let path = args[1]
let url = URL(fileURLWithPath: path)

guard let nsImage = NSImage(contentsOf: url),
      let cgImage = nsImage.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    print("Failed to load image"); exit(1)
}

let request = VNRecognizeTextRequest()
request.recognitionLevel = .accurate
request.recognitionLanguages = ["zh-Hans", "en"]

let handler = VNImageRequestHandler(cgImage: cgImage)
try? handler.perform([request])

for observation in request.results ?? [] {
    if let candidate = observation.topCandidates(1).first {
        print(candidate.string)
    }
}
