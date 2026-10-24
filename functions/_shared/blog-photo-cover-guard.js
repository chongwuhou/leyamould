// Five approved source-owned photo choices. Never accept caller-supplied cover URLs.
export const PHOTO_COVERS = Object.freeze({
  "water-bottle-cap-types-bulk-guide": ["/assets/blog/water-bottle-cap-types-bulk-20261016.webp","/assets/curated-hd/feature-flip-top.webp"],
  "bottle-factory-rfq-template": ["/assets/blog/bottle-factory-rfq-template-20261016.webp","/assets/lo/detail/lo-002-lifestyle.webp"],
  "outdoor-tour-operator-group-water-bottle-wholesale": ["/assets/blog/water-bottle-capacity-guide-20261017.webp","/assets/lo/detail/lo-004-lifestyle.webp"],
  "supplement-brand-shaker-bottle-bundle-oem-sourcing": ["/assets/blog/replacement-water-bottle-lids-20261017.webp","/assets/sku-hd/slide-094-gpt-reviewed-20261013.webp"],
  "trade-show-promotional-water-bottle-deadline-procurement": ["/assets/blog/water-bottle-sample-approval-20261017.webp","/assets/lo/detail/lo-005-lifestyle.webp"]
});
export const PHOTO_SLUGS=Object.freeze(Object.keys(PHOTO_COVERS));
export const PHOTO_LANGS=Object.freeze(["es","pt","ru","tr"]);
const CARD='<article class="news-card">';
export function changeBlogPostCover(post,slug){
  const choice=PHOTO_COVERS[slug];if(!choice)return post;
  const [oldCover,newCover]=choice;
  // Owner changed to a different image; preserve it verbatim.
  return post.cover===oldCover?{...post,cover:newCover}:post;
}
export function changeLocalizedBlogHero(mainHtml,slug){
  const choice=PHOTO_COVERS[slug];if(!choice)return mainHtml;
  const [oldCover,newCover]=choice;
  const old='<div class="blog-detail__cover"><img src="'+oldCover+'"';
  return mainHtml.includes(old)?mainHtml.replace(old,'<div class="blog-detail__cover"><img src="'+newCover+'"'):mainHtml;
}
export function changeLocalizedIndex(mainHtml,activeSlugs){
  const segments=mainHtml.split(CARD);
  for(let i=1;i<segments.length;i++){
    const end=segments[i].indexOf('</article>');if(end<0)continue;
    let card=segments[i].slice(0,end);
    for(const slug of activeSlugs){
      const choice=PHOTO_COVERS[slug];if(!choice)continue;
      if(!card.includes('href="/blog/'+slug+'/"'))continue;
      const [oldCover,newCover]=choice;
      // Restrict this edit to the target card's image src, not related text.
      const old='src="'+oldCover+'"';
      if(card.includes(old))card=card.replace(old,'src="'+newCover+'"');
    }
    segments[i]=card+segments[i].slice(end);
  }
  return segments.join(CARD);
}
