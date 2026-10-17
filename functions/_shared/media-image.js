// Shared image validation for XUYI blog, product and page R2 media.
export const IMAGE_TYPES = new Map([
  ["image/jpeg","jpg"],["image/png","png"],["image/webp","webp"]
]);
export async function checkedImage(file) {
  if (!(file instanceof File) || !IMAGE_TYPES.has(file.type) ||
      file.size < 200 || file.size > 6 * 1024 * 1024) {
    throw new Error("Only JPEG, PNG and WebP images up to 6MB are allowed");
  }
  const buffer = await file.arrayBuffer();
  const b = new Uint8Array(buffer);
  const valid = file.type === "image/jpeg"
    ? b[0] === 255 && b[1] === 216 && b[2] === 255
    : file.type === "image/png"
    ? b[0] === 137 && b[1] === 80 && b[2] === 78 && b[3] === 71
    : String.fromCharCode(...b.slice(0,4)) === "RIFF" &&
      String.fromCharCode(...b.slice(8,12)) === "WEBP";
  if (!valid) throw new Error("Image content does not match MIME type");
  return {buffer,extension:IMAGE_TYPES.get(file.type),type:file.type};
}
