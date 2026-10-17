// Dimensions are extracted from image headers, without external processors.
// The parser intentionally rejects unsupported/corrupt headers.
const u16=(b,i)=>((b[i]<<8)|b[i+1])>>>0;
const u32=(b,i)=>((b[i]*16777216)+(b[i+1]<<16)+(b[i+2]<<8)+b[i+3])>>>0;
const le16=(b,i)=>b[i]|(b[i+1]<<8);
const le24=(b,i)=>b[i]|(b[i+1]<<8)|(b[i+2]<<16);
const magic=(b,i,s)=>[...s].every((c,x)=>b[i+x]===c.charCodeAt(0));
export function imageDimensions(buffer,type){
 const b=new Uint8Array(buffer);let width=0,height=0;
 if(type==="image/png"&&b.length>=24&&b[0]===137&&magic(b,12,"IHDR")){
  width=u32(b,16);height=u32(b,20);
 }else if(type==="image/jpeg"&&b.length>=12&&b[0]===255&&b[1]===216){
  for(let i=2;i+9<b.length;){
   if(b[i++]!==255)break;
   while(b[i]===255)i++;
   const code=b[i++];if(code===0xda||code===0xd9)break;
   if(code===0xd8||code===0x01)continue;
   if(i+2>b.length)break;
   const len=u16(b,i);if(len<2||i+len>b.length)break;
   if([0xc0,0xc1,0xc2,0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf].includes(code)){
    if(len<7)break;
    height=u16(b,i+3);width=u16(b,i+5);break;
   }i+=len;
  }
 }else if(type==="image/webp"&&b.length>=30&&magic(b,0,"RIFF")&&magic(b,8,"WEBP")){
  if(magic(b,12,"VP8X")){width=le24(b,24)+1;height=le24(b,27)+1}
  else if(magic(b,12,"VP8L")&&b[20]===0x2f){
   width=1+((b[21]|((b[22]&0x3f)<<8))>>>0);
   height=1+(((b[22]>>6)|(b[23]<<2)|((b[24]&0xf)<<10))>>>0);
  }else if(magic(b,12,"VP8 ")&&b.length>=30&&b[23]===0x9d&&b[24]===0x01&&b[25]===0x2a){
   width=le16(b,26)&0x3fff;height=le16(b,28)&0x3fff;
  }
 }
 if(!width||!height||width>15000||height>15000||width*height>100_000_000)throw Error("Cannot verify image pixel dimensions");
 return {width,height};
}
export function mimeOfName(filename){
 if(filename.endsWith(".webp"))return "image/webp";
 if(filename.endsWith(".png"))return "image/png";
 if(filename.endsWith(".jpg"))return "image/jpeg";
 return null;
}
