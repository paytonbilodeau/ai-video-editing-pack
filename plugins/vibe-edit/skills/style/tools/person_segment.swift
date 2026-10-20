import Foundation
import AVFoundation
import Vision
import CoreImage

let args = CommandLine.arguments
guard args.count == 5, let maskWidth=Int(args[3]), let maskHeight=Int(args[4]), maskWidth>0, maskHeight>0 else { print("usage: person_segment.swift upright-source.mp4 new-mask.mov width height"); exit(1) }
guard !FileManager.default.fileExists(atPath: args[2]) else { print("Output exists"); exit(2) }
let asset = AVURLAsset(url: URL(fileURLWithPath: args[1]))
let out = URL(fileURLWithPath: args[2])
guard let track = asset.tracks(withMediaType: .video).first else { fatalError("No video track") }
guard track.preferredTransform == .identity else { fatalError("Normalize orientation into a new upright working copy first") }
let reader = try AVAssetReader(asset: asset)
let input = AVAssetReaderTrackOutput(track: track, outputSettings: [kCVPixelBufferPixelFormatTypeKey as String: kCVPixelFormatType_32BGRA])
reader.add(input)
let writer = try AVAssetWriter(outputURL: out, fileType: .mov)
let w = maskWidth, h = maskHeight
let output = AVAssetWriterInput(mediaType: .video, outputSettings: [AVVideoCodecKey: AVVideoCodecType.proRes422, AVVideoWidthKey:w, AVVideoHeightKey:h])
let adaptor = AVAssetWriterInputPixelBufferAdaptor(assetWriterInput: output, sourcePixelBufferAttributes: [kCVPixelBufferPixelFormatTypeKey as String:kCVPixelFormatType_32BGRA, kCVPixelBufferWidthKey as String:w, kCVPixelBufferHeightKey as String:h, kCVPixelBufferIOSurfacePropertiesKey as String: [:]])
writer.add(output)
writer.startWriting(); writer.startSession(atSourceTime: .zero); reader.startReading()
let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8
let handler = VNSequenceRequestHandler()
let context = CIContext(options:[.cacheIntermediates:false])
let cs = CGColorSpaceCreateDeviceRGB()
var frame = 0
var boxes:[[String:Any]]=[]
let cuts:Set<Int> = []
while let sample = input.copyNextSampleBuffer() {
 try autoreleasepool {
  guard let buffer = CMSampleBufferGetImageBuffer(sample) else {fatalError("Missing input")}
  try handler.perform([request], on: buffer, orientation: .up)
  guard let mask = request.results?.first?.pixelBuffer else {fatalError("Missing mask")}
  let original = CIImage(cvPixelBuffer:mask)
  let image = original.transformed(by:CGAffineTransform(scaleX:CGFloat(w)/original.extent.width,y:CGFloat(h)/original.extent.height))
  var pb:CVPixelBuffer?
  CVPixelBufferPoolCreatePixelBuffer(kCFAllocatorDefault,adaptor.pixelBufferPool!, &pb)
  guard let result=pb else {fatalError("Missing output")}
  context.render(image,to:result,bounds:CGRect(x:0,y:0,width:w,height:h),colorSpace:cs)
  while !output.isReadyForMoreMediaData { Thread.sleep(forTimeInterval:0.002) }
  if !adaptor.append(result,withPresentationTime:CMSampleBufferGetPresentationTimeStamp(sample)) {fatalError("Append failed")}
  if frame%90 == 0 || cuts.contains(frame) {
   let face=VNDetectFaceRectanglesRequest()
   try VNImageRequestHandler(cvPixelBuffer:buffer,orientation:.up).perform([face])
   boxes.append(["frame":frame,"faces":(face.results ?? []).map {o in ["x":o.boundingBox.minX,"y":1-o.boundingBox.maxY,"w":o.boundingBox.width,"h":o.boundingBox.height]}])
  }
  if frame%300 == 0 {print("frame \(frame), mask \(CVPixelBufferGetWidth(mask))x\(CVPixelBufferGetHeight(mask))");fflush(stdout)}
  frame += 1
 }
}
output.markAsFinished()
let sem = DispatchSemaphore(value:0);writer.finishWriting{sem.signal()};sem.wait()
try JSONSerialization.data(withJSONObject:boxes,options:.prettyPrinted).write(to:out.deletingPathExtension().appendingPathExtension("faces.json"))
print("Complete: \(frame) frames, writer \(writer.status.rawValue)")
if writer.status != .completed {fatalError("\(String(describing:writer.error))")}
