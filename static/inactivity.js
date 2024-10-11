// 순서 상관없이 랜덤하게 띄우기

let timeout;
let adTimeout;

function resetTimer() {
    clearTimeout(timeout);
    clearTimeout(adTimeout);
    timeout = setTimeout(showRandomAd, 10000);  // 10 seconds of inactivity to show the first ad
}

function showRandomAd() {
    const ads = [
        {id: 'banner1', content: `<h2>광고 배너 1</h2><p>이것은 광고입니다.</p><img src="/static/ad_image_1.jpg" alt="Ad Image 1">`},
        {id: 'banner2', content: `<h2>광고 배너 2</h2><p>이것은 광고입니다.</p><img src="/static/ad_image_2.jpg" alt="Ad Image 2">`},
        {id: 'banner3', content: `<h2>광고 배너 3</h2><p>이것은 광고입니다.</p><img src="/static/ad_image_3.jpg" alt="Ad Image 3">`}
    ];
    
    const currentAdId = document.querySelector('.ad-banner')?.id;
    const remainingAds = ads.filter(ad => ad.id !== currentAdId);
    const randomAd = remainingAds[Math.floor(Math.random() * remainingAds.length)];

    displayAd(randomAd.id, randomAd.content);
}

function showNextAd() {
    showRandomAd();
}

function displayAd(adId, content) {
    removeAds();
    const adBanner = document.createElement('div');
    adBanner.id = adId;
    adBanner.classList.add('ad-banner');
    adBanner.innerHTML = content + `<button class="btn" onclick="removeAds()">돌아가기</button>`;
    document.body.appendChild(adBanner);
    
    adTimeout = setTimeout(showNextAd, 10000);  // 10 seconds of inactivity to show the next ad
}

function removeAds() {
    const ads = document.querySelectorAll('.ad-banner');
    ads.forEach(ad => ad.remove());
}

window.onload = resetTimer;
document.onmousemove = resetTimer;
document.onkeydown = resetTimer;
document.ontouchstart = resetTimer;