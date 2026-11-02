// Adapted from recovered Product Design render functions. See docs/m8/pr7/prototype12.
// No source clocks, controls, event handlers, eval, or HTML injection.
export function clip01(root) {
    const $ = id => root.querySelector('#' + id);
    const ov = $('krtr-overview'), setup = $('krtr-setup'), pop = $('krtr-pop');
    const demo = $('krtr-profile-demo'), man = $('krtr-profile-manufacturer');
    const ph = $('krtr-profile-hover'), mh = $('krtr-man-hover');
    const cursor = $('krtr-cursor'), ring = $('krtr-click');
    let t = 0;
    const manualHover = false;
    const clamp = x => Math.min(1, Math.max(0, x));
    const bezier = (a, b, c, d, u) => { let q = 1 - u; return q * q * q * a + 3 * q * q * u * b + 3 * q * u * u * c + u * u * u * d; };
    function timing(x1, y1, x2, y2, p) {
        p = clamp(p);
        let low = 0, high = 1;
        for (let i = 0; i < 20; i++) {
            let mid = (low + high) / 2;
            if (bezier(0, x1, x2, 1, mid) < p)
                low = mid;
            else
                high = mid;
        }
        return bezier(0, y1, y2, 1, (low + high) / 2);
    }
    const sfsl = p => timing(.45, 0, .23, 1, p);
    const out = p => timing(.12, .75, .22, 1, p);
    const fade = (a, b) => out((t - a) / (b - a));
    const path = (p0, p1, p2, p3, k) => ({
        x: bezier(p0.x, p1.x, p2.x, p3.x, k),
        y: bezier(p0.y, p1.y, p2.y, p3.y, k)
    });
    function cursorPosition() {
        if (t < 850)
            return { x: 803, y: 436 };
        if (t < 1810)
            return path({ x: 803, y: 436 }, { x: 677, y: 487 }, { x: 298, y: 560 }, { x: 80, y: 583 }, sfsl((t - 850) / 960));
        if (t < 3130)
            return { x: 80, y: 583 };
        if (t < 3610)
            return path({ x: 80, y: 583 }, { x: 79, y: 558 }, { x: 111, y: 499 }, { x: 126, y: 477 }, sfsl((t - 3130) / 480));
        return { x: 126, y: 477 };
    }
    function render() {
        let next = fade(4170, 4460), prev = 1 - fade(4070, 4290);
        ov.setAttribute('opacity', String(prev));
        setup.setAttribute('opacity', String(next));
        demo.setAttribute('opacity', String(prev));
        man.setAttribute('opacity', String(next));
        let showMenu = fade(2270, 2510) * (1 - fade(3950, 4130));
        pop.setAttribute('opacity', String(showMenu));
        pop.setAttribute('transform', 'translate(0 ' + ((1 - fade(2270, 2510)) * 7).toFixed(2) + ')');
        mh.setAttribute('opacity', String(manualHover || (t >= 3550 && t < 3990) ? fade(3480, 3610) : 0));
        let hoverDemo = t >= 1760 && t < 2290;
        ph.setAttribute('opacity', String(hoverDemo ? fade(1670, 1800) * .95 : 0));
        let pos = cursorPosition();
        let cursorFade = t < 4140 ? 1 : 1 - fade(4100, 4300);
        cursor.setAttribute('opacity', String(cursorFade));
        cursor.setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        let click1 = t >= 2120 && t <= 2320;
        let click2 = t >= 3850 && t <= 4010;
        let clickNow = click1 || click2;
        let c = click1 ? { x: 80, y: 583 } : { x: 126, y: 477 };
        ring.setAttribute('transform', `translate(${c.x} ${c.y})`);
        let cp = click1 ? (t - 2120) / 200 : (t - 3850) / 160;
        ring.setAttribute('opacity', clickNow ? String((1 - clamp(cp)) * .8) : '0');
        ring.querySelector('circle').setAttribute('r', String(12 + 18 * clamp(cp)));
    }
    return (time) => { t = time; render(); };
}
export function clip02(root) {
    const $ = id => root.querySelector('#' + id);
    const draft = $('kr23draft'), created = $('kr23created'), invite = $('kr23invite');
    const popup = $('kr23popup'), hover = $('kr23logHover'), profileHover = $('kr23profileHover');
    const pm = $('kr23profileM'), pl = $('kr23profileL');
    const buttonHover = $('kr23buttonHover'), buttonNormal = $('kr23buttonNormal'), buttonBusy = $('kr23buttonBusy');
    const cursor = $('kr23cursor'), ripple = $('kr23click');
    let t = 0;
    const menuManual = false;
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function easing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let a = 0, b = 1;
        for (let i = 0; i < 18; i++) {
            let m = (a + b) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                a = m;
            else
                b = m;
        }
        return cubic(0, y1, y2, 1, (a + b) / 2);
    }
    const motion = (a, b) => easing((t - a) / (b - a));
    const fade = (a, b) => easing((t - a) / (b - a), .15, .3, .25, 1);
    function curve(a, b, c, d, p) {
        return { x: cubic(a.x, b.x, c.x, d.x, p), y: cubic(a.y, b.y, c.y, d.y, p) };
    }
    function pointer() {
        if (t < 640)
            return { x: 862, y: 464 };
        if (t < 1580)
            return curve({ x: 862, y: 464 }, { x: 814, y: 469 }, { x: 725, y: 496 }, { x: 651, y: 506 }, motion(640, 1580));
        if (t < 3390)
            return { x: 651, y: 506 };
        if (t < 4300)
            return curve({ x: 651, y: 506 }, { x: 501, y: 541 }, { x: 267, y: 602 }, { x: 81, y: 585 }, motion(3390, 4300));
        if (t < 5080)
            return { x: 81, y: 585 };
        if (t < 5590)
            return curve({ x: 81, y: 585 }, { x: 79, y: 540 }, { x: 125, y: 490 }, { x: 127, y: 471 }, motion(5080, 5590));
        return { x: 127, y: 471 };
    }
    function render() {
        const a = fade(2370, 2640);
        const b = fade(6060, 6350);
        draft.setAttribute('opacity', String(1 - a));
        created.setAttribute('opacity', String(a * (1 - b)));
        invite.setAttribute('opacity', String(b));
        const pc = fade(6110, 6380);
        pm.setAttribute('opacity', String(1 - pc));
        pl.setAttribute('opacity', String(pc));
        const busy = fade(2040, 2140);
        buttonNormal.setAttribute('opacity', String(1 - busy));
        buttonBusy.setAttribute('opacity', String(busy));
        buttonHover.setAttribute('opacity', String(t >= 1550 && t < 2040 ? fade(1510, 1690) : 0));
        const profileHighlight = t >= 4250 && t < 4660;
        profileHover.setAttribute('opacity', String(profileHighlight ? fade(4170, 4300) : 0));
        let menuVisible = fade(4690, 4900) * (1 - fade(5890, 6090));
        popup.setAttribute('opacity', String(menuVisible));
        popup.setAttribute('transform', 'translate(0 ' + (7 * (1 - fade(4690, 4900))).toFixed(2) + ')');
        const menuHover = (t > 5520 && t < 5950);
        hover.setAttribute('opacity', String(menuManual || menuHover ? fade(5440, 5610) : 0));
        popup.style.pointerEvents = (t >= 4760 && t < 5950) ? 'auto' : 'none';
        const pos = pointer();
        let visibility = t < 6210 ? 1 : 1 - fade(6190, 6440);
        cursor.setAttribute('opacity', String(visibility));
        cursor.setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        const taps = [
            { a: 1900, b: 2040, x: 651, y: 506 },
            { a: 4540, b: 4660, x: 81, y: 585 },
            { a: 5800, b: 5940, x: 127, y: 471 }
        ];
        let active = taps.find(k => t >= k.a && t < k.b);
        if (active) {
            let p = clamp((t - active.a) / (active.b - active.a));
            ripple.setAttribute('opacity', String((1 - p) * .65));
            ripple.setAttribute('transform', `translate(${active.x} ${active.y})`);
            ripple.querySelector('circle').setAttribute('r', String(9 + p * 16));
        }
        else
            ripple.setAttribute('opacity', '0');
    }
    return (time) => { t = time; render(); };
}
export function clip03(root) {
    const $ = id => root.querySelector('#' + id);
    const inv = $('kr34inv'), room = $('kr34room'), datasets = $('kr34datasetsNav');
    const rows1 = $('kr34rows1'), rows2 = $('kr34rows2'), actions = $('kr34roomActions');
    const hover = $('kr34btnHover'), normal = $('kr34btnNormal'), busy = $('kr34btnBusy'), spinner = $('kr34spinner');
    const connectHover = $('kr34connectHover'), cursor = $('kr34cursor'), ripple = $('kr34click');
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { let v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function bezierEase(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let low = 0, high = 1;
        for (let i = 0; i < 20; i++) {
            let m = (low + high) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                low = m;
            else
                high = m;
        }
        return cubic(0, y1, y2, 1, (low + high) / 2);
    }
    const ease = (a, b) => bezierEase((t - a) / (b - a));
    const fade = (a, b) => bezierEase((t - a) / (b - a), .15, .25, .23, 1);
    function curve(a, b, c, d, p) {
        return { x: cubic(a.x, b.x, c.x, d.x, p), y: cubic(a.y, b.y, c.y, d.y, p) };
    }
    function pointer() {
        if (t < 480)
            return { x: 953, y: 439 };
        if (t < 1460)
            return curve({ x: 953, y: 439 }, { x: 854, y: 438 }, { x: 735, y: 500 }, { x: 627, y: 500 }, ease(480, 1460));
        if (t < 4060)
            return { x: 627, y: 500 };
        if (t < 5290)
            return curve({ x: 627, y: 500 }, { x: 705, y: 479 }, { x: 842, y: 475 }, { x: 949, y: 500 }, ease(4060, 5290));
        return { x: 949, y: 500 };
    }
    function render() {
        const switching = fade(2700, 3030);
        inv.setAttribute('opacity', String(1 - switching));
        room.setAttribute('opacity', String(switching));
        datasets.setAttribute('opacity', String(fade(3090, 3410)));
        rows1.setAttribute('opacity', String(fade(3150, 3420)));
        rows2.setAttribute('opacity', String(fade(3340, 3610)));
        actions.setAttribute('opacity', String(fade(3490, 3760)));
        hover.setAttribute('opacity', String(t >= 1440 && t < 2050 ? fade(1380, 1570) : 0));
        const loading = fade(2040, 2150);
        normal.setAttribute('opacity', String(1 - loading));
        busy.setAttribute('opacity', String(loading));
        spinner.setAttribute('transform', `rotate(${(t * 0.22).toFixed(1)} 564 500)`);
        connectHover.setAttribute('opacity', String(t > 5340 ? fade(5330, 5510) : 0));
        let pos = pointer();
        const mouseOpacity = t < 2800 ? 1 : t < 3850 ? 1 - fade(2780, 3040) : fade(3750, 3990);
        cursor.setAttribute('opacity', String(mouseOpacity));
        cursor.setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        if (t >= 1960 && t < 2150) {
            const p = clamp((t - 1960) / 190);
            ripple.setAttribute('opacity', String((1 - p) * .65));
            ripple.setAttribute('transform', 'translate(627 500)');
            ripple.querySelector('circle').setAttribute('r', String(9 + p * 17));
        }
        else
            ripple.setAttribute('opacity', '0');
    }
    return (time) => { t = time; render(); };
}
export function clip04(root) {
    const $ = id => root.querySelector('#' + id);
    const room = $('kr45room'), protect = $('kr45protect'), rnav = $('kr45roomsNav'), dnav = $('kr45datasetsNav');
    const normal = $('kr45buttonNormal'), busy = $('kr45buttonBusy'), hover = $('kr45buttonHover'), spinner = $('kr45spinner');
    const cursor = $('kr45cursor'), ripple = $('kr45click'), hit = $('kr45hit');
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function curveEase(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let a = 0, b = 1;
        for (let i = 0; i < 18; i++) {
            const m = (a + b) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                a = m;
            else
                b = m;
        }
        return cubic(0, y1, y2, 1, (a + b) / 2);
    }
    const move = (a, b) => curveEase((t - a) / (b - a));
    const fade = (a, b) => curveEase((t - a) / (b - a), .16, .45, .24, 1);
    function path(a, b, c, d, k) { return { x: cubic(a.x, b.x, c.x, d.x, k), y: cubic(a.y, b.y, c.y, d.y, k) }; }
    function pointer() {
        if (t < 550)
            return { x: 981, y: 399 };
        if (t < 1570)
            return path({ x: 981, y: 399 }, { x: 967, y: 453 }, { x: 910, y: 482 }, { x: 869, y: 501 }, move(550, 1570));
        return { x: 869, y: 501 };
    }
    function pct(element, value) {
        $(element).textContent = Math.round(value) + '%';
    }
    const original1 = '3B7E4D10C8A65F902D31B7C4E8F65A0D912B43E5C6';
    const original2 = '9C6E20A4F1D85B37E0C92A5F41D7B83C605E19A4D2';
    const hexdigits = '0123456789ABCDEF';
    function scramble(input, seed) {
        let result = '';
        for (let i = 0; i < input.length; i++) {
            const mutate = (i * 17 + Math.floor(seed * 9)) % 11 === 0;
            result += mutate ? hexdigits[(i * 7 + Math.floor(seed * 4)) % 16] : input[i];
        }
        return result;
    }
    function render() {
        const switched = fade(2700, 3000);
        room.setAttribute('opacity', String(1 - switched));
        protect.setAttribute('opacity', String(switched));
        rnav.setAttribute('opacity', String(1 - switched));
        dnav.setAttribute('opacity', String(switched));
        const loading = fade(2130, 2240);
        normal.setAttribute('opacity', String(1 - loading));
        busy.setAttribute('opacity', String(loading));
        spinner.setAttribute('transform', `rotate(${(t * .28).toFixed(1)} 818 503)`);
        hover.setAttribute('opacity', String(t > 1560 && t < 2210 ? fade(1540, 1710) : 0));
        const p1 = move(3220, 4800);
        const p2 = move(3520, 5350);
        const l1 = Math.min(.73, move(3520, 10300));
        const l2 = Math.min(.61, move(3990, 10900));
        for (const [name, p] of [['mBar1', p1], ['mBar2', p2], ['lBar1', l1], ['lBar2', l2]]) {
            $('kr45' + name).setAttribute('width', String(365 * p));
        }
        for (const [name, p] of [['mPct1', p1], ['mPct2', p2], ['lPct1', l1], ['lPct2', l2]])
            pct('kr45' + name, p * 100);
        const complete = t >= 5390;
        $('kr45mStatus').textContent = complete ? 'Protected' : 'Protecting';
        $('kr45mStatus1').textContent = p1 >= 1 ? 'Protected' : 'Protecting';
        $('kr45mStatus2').textContent = p2 >= 1 ? 'Protected' : 'Protecting';
        $('kr45mBadge').setAttribute('fill', complete ? '#3A4852' : '#36383A');
        $('kr45mStatus1').setAttribute('fill', p1 >= 1 ? '#D0E2EC' : '#A4B8C4');
        $('kr45mStatus2').setAttribute('fill', p2 >= 1 ? '#D0E2EC' : '#A4B8C4');
        $('kr45lStatus1').textContent = t < 3600 ? 'Waiting' : 'Protecting';
        $('kr45lStatus2').textContent = t < 4000 ? 'Waiting' : 'Protecting';
        $('kr45lHex1').textContent = t < 3400 ? original1 : scramble(original1, t / 120);
        $('kr45lHex2').textContent = t < 3900 ? original2 : scramble(original2, t / 130);
        const pos = pointer();
        cursor.setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        cursor.setAttribute('opacity', String(1 - fade(2730, 3050)));
        if (t >= 2040 && t < 2230) {
            const p = clamp((t - 2040) / 190);
            ripple.setAttribute('opacity', String((1 - p) * .7));
            ripple.setAttribute('transform', 'translate(869 501)');
            ripple.querySelector('circle').setAttribute('r', String(9 + p * 17));
        }
        else
            ripple.setAttribute('opacity', '0');
        hit.style.pointerEvents = t < 2210 ? 'auto' : 'none';
    }
    return (time) => { t = time; render(); };
}
export function clip05(root) {
    const $ = id => root.querySelector('#' + id);
    const protection = $('kr56protection'), library = $('kr56library');
    const dsActive = $('kr56datasetActive'), dsIdle = $('kr56datasetIdle');
    const compIdle = $('kr56compIdle'), compActive = $('kr56compActive'), compHover = $('kr56compHover');
    const pointer = $('kr56pointer'), click = $('kr56click');
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const bez = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function timing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let a = 0, b = 1;
        for (let i = 0; i < 20; i++) {
            const m = (a + b) / 2;
            if (bez(0, x1, x2, 1, m) < p)
                a = m;
            else
                b = m;
        }
        return bez(0, y1, y2, 1, (a + b) / 2);
    }
    const motion = (a, b) => timing((t - a) / (b - a));
    const fade = (a, b) => timing((t - a) / (b - a), .17, .38, .23, 1);
    const route = (a, b, c, d, k) => ({ x: bez(a.x, b.x, c.x, d.x, k), y: bez(a.y, b.y, c.y, d.y, k) });
    const hexchars = '0123456789ABCDEF';
    const str1 = '3B7E4D10C8A65F902D31B7C4E8F65A0D912B43E5C6';
    const str2 = '9C6E20A4F1D85B37E0C92A5F41D7B83C605E19A4D2';
    function cryptoVisual(s, percent, step) {
        if (percent >= .999)
            return s;
        let out = '';
        for (let i = 0; i < s.length; i++) {
            const flash = ((i * 13 + step * 7) % 23) < 2 && percent < .97;
            out += flash ? hexchars[(i * 5 + step) % 16] : s[i];
        }
        return out;
    }
    function cursorPosition() {
        if (t < 3440)
            return { x: 969, y: 451 };
        if (t < 4870)
            return route({ x: 969, y: 451 }, { x: 805, y: 379 }, { x: 398, y: 277 }, { x: 92, y: 293 }, motion(3440, 4870));
        return { x: 92, y: 293 };
    }
    function render() {
        const p1 = .73 + .27 * motion(400, 2400);
        const p2 = .61 + .39 * motion(640, 2790);
        const s1 = p1 >= .999999, s2 = p2 >= .999999;
        const ready = t >= 2820;
        for (const [id, p] of [['kr56bar1', p1], ['kr56bar2', p2]]) {
            $(id).setAttribute('width', String(365 * p));
        }
        $('kr56pct1').textContent = Math.round(p1 * 100) + '%';
        $('kr56pct2').textContent = Math.round(p2 * 100) + '%';
        $('kr56status1').textContent = s1 ? 'Protected' : 'Protecting';
        $('kr56status2').textContent = s2 ? 'Protected' : 'Protecting';
        $('kr56hex1').textContent = cryptoVisual(str1, p1, Math.floor(t / 130));
        $('kr56hex2').textContent = cryptoVisual(str2, p2, Math.floor(t / 140));
        $('kr56badgeText').textContent = ready ? 'Protected' : 'Protecting';
        $('kr56badgeBG').setAttribute('fill', ready ? '#3A4852' : '#35434D');
        $('kr56subStatus').textContent = ready ? 'Protected within its own environment' : 'Preparing locally · Your organization';
        $('kr56topStatus').textContent = ready ? 'All inputs protected' : 'Protection in progress';
        $('kr56footL').textContent = ready ? 'Local inputs protected · Ready for computation' : 'Protected locally before private execution';
        const switchP = fade(5490, 5790);
        protection.setAttribute('opacity', String(1 - switchP));
        library.setAttribute('opacity', String(switchP));
        dsActive.setAttribute('opacity', String(1 - switchP));
        dsIdle.setAttribute('opacity', String(switchP));
        compIdle.setAttribute('opacity', String(fade(2960, 3240) * (1 - switchP)));
        compActive.setAttribute('opacity', String(switchP));
        compHover.setAttribute('opacity', String(t >= 4780 && t < 5520 ? fade(4740, 4940) : 0));
        const mouse = cursorPosition();
        pointer.setAttribute('transform', `translate(${mouse.x.toFixed(2)} ${mouse.y.toFixed(2)})`);
        pointer.setAttribute('opacity', String(1 - fade(5640, 5920)));
        if (t >= 5320 && t < 5500) {
            const p = clamp((t - 5320) / 180);
            click.setAttribute('transform', 'translate(92 293)');
            click.setAttribute('opacity', String((1 - p) * .65));
            click.querySelector('circle').setAttribute('r', String(9 + p * 17));
        }
        else
            click.setAttribute('opacity', '0');
    }
    return (time) => { t = time; render(); };
}
export function clip06(root) {
    const $ = id => root.querySelector('#' + id);
    const library = $('kr67library'), execution = $('kr67execution'), cursor = $('kr67cursor');
    const click = $('kr67click'), normal = $('kr67buttonNormal'), busy = $('kr67buttonBusy');
    const hit = $('kr67hit');
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function easing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let lo = 0, hi = 1;
        for (let i = 0; i < 18; i++) {
            let m = (lo + hi) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                lo = m;
            else
                hi = m;
        }
        return cubic(0, y1, y2, 1, (lo + hi) / 2);
    }
    const motion = (a, b) => easing((t - a) / (b - a));
    const fade = (a, b) => easing((t - a) / (b - a), .14, .32, .24, 1);
    const route = (a, b, c, d, p) => ({ x: cubic(a.x, b.x, c.x, d.x, p), y: cubic(a.y, b.y, c.y, d.y, p) });
    function position() {
        if (t < 490)
            return { x: 670, y: 456 };
        if (t < 1470)
            return route({ x: 670, y: 456 }, { x: 742, y: 463 }, { x: 875, y: 500 }, { x: 957, y: 513 }, motion(490, 1470));
        return { x: 957, y: 513 };
    }
    function setOpacity(id, v) { $(id).setAttribute('opacity', String(clamp(v))); }
    function render() {
        const change = fade(2620, 2920);
        library.setAttribute('opacity', String(1 - change));
        execution.setAttribute('opacity', String(change));
        hit.style.pointerEvents = t < 2190 ? 'auto' : 'none';
        setOpacity('kr67hover', t >= 1440 && t < 2200 ? fade(1390, 1560) * (1 - fade(2100, 2230)) : 0);
        const load = fade(2050, 2150);
        normal.setAttribute('opacity', String(1 - load));
        busy.setAttribute('opacity', String(load));
        $('kr67buttonSpinner').setAttribute('transform', `rotate(${(t * .24).toFixed(1)} 916 514)`);
        const pos = position();
        cursor.setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        cursor.setAttribute('opacity', String(1 - fade(2770, 3090)));
        if (t >= 1940 && t < 2130) {
            const p = clamp((t - 1940) / 190);
            click.setAttribute('transform', 'translate(957 513)');
            click.setAttribute('opacity', String((1 - p) * .7));
            click.querySelector('circle').setAttribute('r', String(9 + 17 * p));
        }
        else
            click.setAttribute('opacity', '0');
        const s1active = t >= 3110 && t < 3900, s1done = t >= 3900;
        const s2active = t >= 3900 && t < 4850, s2done = t >= 4850;
        const s3active = t >= 4990;
        $('kr67dot1').setAttribute('fill', s1done ? '#3C4C56' : s1active ? '#394651' : '#36383B');
        $('kr67dot2').setAttribute('fill', s2done ? '#3C4C56' : s2active ? '#394651' : '#36383B');
        $('kr67dot3').setAttribute('fill', s3active ? '#394B58' : '#36383B');
        setOpacity('kr67check1', s1done ? 1 : 0);
        setOpacity('kr67check2', s2done ? 1 : 0);
        setOpacity('kr67spin1', s1active ? 1 : 0);
        setOpacity('kr67spin2', s2active ? 1 : 0);
        setOpacity('kr67spin3', s3active ? 1 : 0);
        for (const [id, x, y] of [['kr67spin1', 249, 292, s1active], ['kr67spin2', 249, 350, s2active], ['kr67spin3', 249, 410, s3active]]) {
            $(id).setAttribute('transform', `rotate(${(t * .22).toFixed(1)} ${x} ${y})`);
        }
        $('kr67s1').textContent = s1done ? 'Complete' : s1active ? 'Checking' : 'Pending';
        $('kr67s2').textContent = s2done ? 'Complete' : s2active ? 'Working' : 'Pending';
        $('kr67s3').textContent = s3active ? 'Working' : 'Pending';
        $('kr67s1').setAttribute('fill', s1done ? '#C6DAE7' : '#A4A7AC');
        $('kr67s2').setAttribute('fill', s2done ? '#C6DAE7' : '#A4A7AC');
        $('kr67s3').setAttribute('fill', s3active ? '#C6DAE7' : '#A4A7AC');
        $('kr67row1').setAttribute('stroke', s1active ? '#6B8394' : '#444447');
        $('kr67row2').setAttribute('stroke', s2active ? '#6B8394' : '#444447');
        $('kr67row3').setAttribute('stroke', s3active ? '#657F91' : '#444447');
        $('kr67row3').setAttribute('fill', s3active ? '#30383E' : '#2E2E30');
        const process = s3active ? Math.min(.67, .67 * motion(4990, 8500)) : 0;
        $('kr67progress').setAttribute('width', String(438 * process));
        $('kr67engineBar').setAttribute('width', String(251 * process));
        $('kr67engineSpin').setAttribute('transform', `rotate(${(t * .19).toFixed(1)} 804 391)`);
        $('kr67headPulse').setAttribute('opacity', String(.65 + .35 * Math.sin(t / 250) * Math.sin(t / 250)));
        const elapsed = Math.min(12, Math.floor(Math.max(0, t - 2930) / 450));
        $('kr67elapsed').textContent = '00:' + String(elapsed).padStart(2, '0');
    }
    return (time) => { t = time; render(); };
}
export function clip07(root) {
    const $ = id => root.querySelector('#' + id);
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const bez = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function ease(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let lo = 0, hi = 1;
        for (let i = 0; i < 19; i++) {
            const m = (lo + hi) / 2;
            if (bez(0, x1, x2, 1, m) < p)
                lo = m;
            else
                hi = m;
        }
        return bez(0, y1, y2, 1, (lo + hi) / 2);
    }
    const motion = (a, b) => ease((t - a) / (b - a));
    const fade = (a, b) => ease((t - a) / (b - a), .14, .42, .24, 1);
    const route = (a, b, c, d, k) => ({ x: bez(a.x, b.x, c.x, d.x, k), y: bez(a.y, b.y, c.y, d.y, k) });
    function point() {
        if (t < 4420)
            return { x: 916, y: 493 };
        if (t < 5570)
            return route({ x: 916, y: 493 }, { x: 725, y: 471 }, { x: 344, y: 315 }, { x: 97, y: 344 }, motion(4420, 5570));
        return { x: 97, y: 344 };
    }
    function op(id, v) { $(id).setAttribute('opacity', String(clamp(v))); }
    function render() {
        const p3 = .67 + .33 * motion(360, 2140);
        const s3done = t >= 2150;
        const s4working = t >= 2590 && t < 3570;
        const allDone = t >= 3570;
        $('kr78bar').setAttribute('width', String(438 * p3));
        $('kr78engineBar').setAttribute('width', String(251 * p3));
        $('kr78s3').textContent = s3done ? 'Complete' : 'Working';
        $('kr78s4').textContent = allDone ? 'Complete' : s4working ? 'Working' : 'Pending';
        $('kr78s4').setAttribute('fill', allDone ? '#C6DAE7' : s4working ? '#B7CDDC' : '#89898E');
        $('kr78note4').textContent = allDone ? 'Aggregate result authorized for viewing' : s4working ? 'Checking authorized output policy' : 'Awaiting completion and output authorization';
        $('kr78row3').setAttribute('stroke', s3done ? '#444447' : '#657F91');
        $('kr78row3').setAttribute('fill', s3done ? '#2E2E30' : '#30383E');
        $('kr78row4').setAttribute('stroke', s4working ? '#657F91' : allDone ? '#566A79' : '#404043');
        $('kr78row4').setAttribute('fill', s4working ? '#30383E' : '#29292B');
        $('kr78dot3').setAttribute('fill', s3done ? '#3C4C56' : '#394B58');
        $('kr78dot4').setAttribute('fill', allDone ? '#3C4C56' : s4working ? '#394B58' : '#303034');
        op('kr78check3', s3done ? 1 : 0);
        op('kr78check4', allDone ? 1 : 0);
        op('kr78spin3', s3done ? 0 : 1);
        op('kr78spin4', s4working ? 1 : 0);
        $('kr78spin3').setAttribute('transform', `rotate(${(t * .22).toFixed(1)} 249 410)`);
        $('kr78spin4').setAttribute('transform', `rotate(${(t * .22).toFixed(1)} 249 490)`);
        $('kr78engineSpin').setAttribute('transform', `rotate(${(t * .18).toFixed(1)} 804 391)`);
        op('kr78engineSpin', s3done ? 0 : 1);
        op('kr78engineCheck', s3done ? 1 : 0);
        $('kr78engineSub').textContent = s3done ? 'Aggregate computation complete' : 'Protected inputs · Secure execution';
        $('kr78head').textContent = allDone ? 'Analysis complete' : 'Computation running';
        $('kr78pulse').setAttribute('opacity', String(allDone ? 1 : .7 + .3 * Math.pow(Math.sin(t / 260), 2)));
        $('kr78outputText').textContent = allDone ? 'Authorized aggregate ready' : s4working ? 'Checking output policy' : 'Not yet available';
        $('kr78outputStatus').textContent = allDone ? 'Ready' : s4working ? 'Working' : 'Pending';
        $('kr78outputStatus').setAttribute('fill', allDone ? '#C5DCEB' : '#94969A');
        $('kr78outputBox').setAttribute('stroke', allDone ? '#637F90' : '#48494D');
        const changed = fade(5860, 6170);
        op('kr78execution', 1 - changed);
        op('kr78gallery', changed);
        op('kr78compActive', 1 - changed);
        op('kr78compIdle', changed);
        op('kr78analyticsIdle', 1 - changed);
        op('kr78analyticsActive', changed);
        const navhover = t >= 5440 && t < 5890;
        op('kr78hover', navhover ? fade(5420, 5520) * (1 - fade(5780, 5960)) : 0);
        $('kr78navHit').style.pointerEvents = (t >= 3610 && t < 5860) ? 'auto' : 'none';
        // Cards enter gently, without a camera movement.
        for (const [id, a, b] of [['kr78card1', 5950, 6280], ['kr78card2', 6000, 6340], ['kr78card3', 6050, 6400]]) {
            const p = fade(a, b);
            op(id, p);
            $(id).setAttribute('transform', `translate(0 ${(1 - p) * 5})`);
        }
        const c = point();
        $('kr78cursor').setAttribute('transform', `translate(${c.x.toFixed(2)} ${c.y.toFixed(2)})`);
        op('kr78cursor', fade(4070, 4330) * (1 - fade(5980, 6250)));
        if (t >= 5750 && t < 5950) {
            const p = clamp((t - 5750) / 200);
            $('kr78click').setAttribute('transform', 'translate(97 344)');
            op('kr78click', (1 - p) * .7);
            $('kr78click').querySelector('circle').setAttribute('r', String(9 + 17 * p));
        }
        else
            op('kr78click', 0);
    }
    return (time) => { t = time; render(); };
}
export function clip08(root) {
    const $ = id => root.querySelector('#' + id);
    let t = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function timing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let lo = 0, hi = 1;
        for (let i = 0; i < 19; i++) {
            const mid = (lo + hi) / 2;
            if (cubic(0, x1, x2, 1, mid) < p)
                lo = mid;
            else
                hi = mid;
        }
        return cubic(0, y1, y2, 1, (lo + hi) / 2);
    }
    const motion = (a, b) => timing((t - a) / (b - a));
    const fade = (a, b) => timing((t - a) / (b - a), .15, .45, .24, 1);
    const route = (a, b, c, d, p) => ({ x: cubic(a.x, b.x, c.x, d.x, p), y: cubic(a.y, b.y, c.y, d.y, p) });
    const op = (id, v) => $(id).setAttribute('opacity', String(clamp(v)));
    const line = $('kr89trend');
    const lineLen = line.getTotalLength ? line.getTotalLength() : 540;
    line.setAttribute('stroke-dasharray', String(lineLen));
    function pointer() {
        if (t < 440)
            return { x: 97, y: 344 };
        if (t < 1570)
            return route({ x: 97, y: 344 }, { x: 137, y: 362 }, { x: 226, y: 483 }, { x: 325, y: 490 }, motion(440, 1570));
        if (t < 6150)
            return { x: 325, y: 490 };
        if (t < 7350)
            return route({ x: 325, y: 490 }, { x: 480, y: 462 }, { x: 755, y: 481 }, { x: 930, y: 511 }, motion(6150, 7350));
        return { x: 930, y: 511 };
    }
    function render() {
        const screen = fade(2650, 2930);
        op('kr89gallery', 1 - screen);
        op('kr89overview', screen);
        const entering = fade(3000, 3310);
        op('kr89metrics', entering);
        $('kr89metrics').setAttribute('transform', `translate(0 ${(1 - entering) * 5})`);
        const count = motion(3190, 4290);
        for (const [id, max] of [['kr89total', 12], ['kr89production', 6], ['kr89transit', 4], ['kr89other', 2]]) {
            $(id).textContent = String(Math.round(max * count));
        }
        const chart = motion(3720, 5400);
        line.setAttribute('stroke-dashoffset', String(lineLen * (1 - chart)));
        op('kr89area', chart * .85);
        const dots = $('kr89dots').querySelectorAll('circle');
        dots.forEach((dot, i) => {
            const p = fade(3880 + i * 205, 4070 + i * 205);
            dot.setAttribute('opacity', String(p));
            dot.setAttribute('transform', `translate(0 ${(1 - p) * 3})`);
        });
        for (const [id, max, start, end] of [
            ['kr89bar1', 127.5, 3890, 4900],
            ['kr89bar2', 85, 4010, 5100],
            ['kr89bar3', 42.5, 4130, 5290]
        ]) {
            $(id).setAttribute('width', String(max * motion(start, end)));
        }
        const pos = pointer();
        $('kr89cursor').setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        const visibility = t < 2550 ? 1 : t < 3350 ? 1 - fade(2540, 2950) : fade(5810, 6130);
        op('kr89cursor', visibility);
        op('kr89ctaHover', t >= 1550 && t < 2160 ? fade(1540, 1690) * (1 - fade(2020, 2200)) : 0);
        op('kr89busy', fade(2100, 2200) * (1 - fade(2570, 2740)));
        $('kr89spinner').setAttribute('transform', `rotate(${(t * .25).toFixed(1)} 269 493)`);
        op('kr89detailHover', t >= 7280 ? fade(7260, 7450) : 0);
        if (t >= 2010 && t < 2200) {
            const p = clamp((t - 2010) / 190);
            $('kr89click').setAttribute('transform', 'translate(325 490)');
            op('kr89click', (1 - p) * .68);
            $('kr89click').querySelector('circle').setAttribute('r', String(9 + 17 * p));
        }
        else
            op('kr89click', 0);
        $('kr89hit').style.pointerEvents = t < 2190 ? 'auto' : 'none';
    }
    return (time) => { t = time; render(); };
}
export function clip10(root) {
    const $ = id => root.querySelector('#' + id);
    const clamp = x => Math.max(0, Math.min(1, x));
    const cubic = (a, b, c, d, u) => { const v = 1 - u; return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d; };
    function ease(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let a = 0, b = 1;
        for (let i = 0; i < 18; i++) {
            const m = (a + b) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                a = m;
            else
                b = m;
        }
        return cubic(0, y1, y2, 1, (a + b) / 2);
    }
    let t = 0;
    const fade = (a, b) => ease((t - a) / (b - a), .14, .4, .24, 1);
    const move = (a, b) => ease((t - a) / (b - a));
    const op = (id, p) => $(id).setAttribute('opacity', String(clamp(p)));
    const route = (a, b, c, d, p) => ({ x: cubic(a.x, b.x, c.x, d.x, p), y: cubic(a.y, b.y, c.y, d.y, p) });
    const question = "What's driving our supply chain risks, and what should we do?";
    const typingStart = 2300, typingEnd = 5500;
    const times = [typingStart];
    let w = 0, weights = [];
    for (let i = 0; i < question.length; i++) {
        let z = 12 + (i * 17 % 13) + (question[i] === ' ' ? 6 : 0) + (question[i] === ',' ? 30 : 0);
        weights.push(z);
        w += z;
    }
    let running = typingStart;
    for (const weight of weights) {
        running += (typingEnd - typingStart) * weight / w;
        times.push(running);
    }
    function count() {
        let n = 0;
        while (n < question.length && times[n + 1] <= t)
            n++;
        return n;
    }
    function pointer() {
        if (t < 400)
            return { x: 886, y: 476 };
        if (t < 1000)
            return route({ x: 886, y: 476 }, { x: 904, y: 478 }, { x: 939, y: 500 }, { x: 933, y: 510 }, move(400, 1000));
        if (t < 5650)
            return { x: 933, y: 510 };
        if (t < 6200)
            return route({ x: 635, y: 485 }, { x: 659, y: 475 }, { x: 699, y: 476 }, { x: 720, y: 490 }, move(5650, 6200));
        return { x: 720, y: 490 };
    }
    function render() {
        const swap = fade(1600, 1950);
        op('kr111dashboard', 1 - swap);
        op('kr111ai', swap);
        op('kr111nav0', 1 - swap);
        op('kr111nav1', swap);
        op('kr111hover1', t < 1150 ? fade(890, 1060) : 0);
        $('kr111hit1').style.pointerEvents = t < 1310 ? 'auto' : 'none';
        const n = count();
        const typed = $('kr111typed');
        typed.textContent = question.slice(0, n);
        op('kr111placeholder', t < typingStart ? 1 : 0);
        const width = typed.getComputedTextLength ? typed.getComputedTextLength() : n * 6.1;
        $('kr111caret').setAttribute('d', `M${(246 + width + 2).toFixed(1)} 471 V490`);
        op('kr111caret', t >= typingStart && t < 6360 && Math.sin(t / 175) > -.2 ? 1 : 0);
        const sent = t >= 6560;
        op('kr111compose', 1 - fade(6530, 6710));
        op('kr111after', fade(6530, 6710));
        op('kr111empty', 1 - fade(6500, 6750));
        op('kr111message', fade(6570, 6850));
        op('kr111working', fade(6990, 7300));
        $('kr111sendBG').setAttribute('fill', sent ? '#8a8c8f' : '#f1f0eb');
        op('kr111hover2', t >= 6130 && t < 6510 ? fade(6090, 6240) : 0);
        $('kr111hit2').style.pointerEvents = t >= 5500 && t < 6490 ? 'auto' : 'none';
        const dots = $('kr111dots').querySelectorAll('circle');
        dots.forEach((d, i) => d.setAttribute('opacity', String(.3 + .7 * Math.pow(Math.sin(t / 245 - i * .8), 2))));
        $('kr111workingText').textContent = t >= 8260 ? 'Organizing authorized insights...' : t >= 7650 ? 'Reviewing aggregate risk context...' : 'Analyzing authorized context...';
        const p = pointer();
        $('kr111cursor').setAttribute('transform', `translate(${p.x.toFixed(2)} ${p.y.toFixed(2)})`);
        op('kr111cursor', t < 1550 ? 1 : t < 5600 ? 1 - fade(1520, 1780) : t < 6740 ? fade(5600, 5820) : 1 - fade(6520, 6740));
        let tap = t >= 1140 && t < 1330 ? { at: 1140, x: 933, y: 510 } : t >= 6380 && t < 6570 ? { at: 6380, x: 720, y: 490 } : null;
        if (tap) {
            const u = clamp((t - tap.at) / 190);
            $('kr111ripple').setAttribute('transform', `translate(${tap.x} ${tap.y})`);
            $('kr111ripple').querySelector('circle').setAttribute('r', String(9 + 17 * u));
            op('kr111ripple', (1 - u) * .7);
        }
        else
            op('kr111ripple', 0);
    }
    return (time) => { t = time; render(); };
}
export function clip11(root) {
    const $ = id => root.querySelector('#' + id);
    let t = 0;
    const clamp = v => Math.max(0, Math.min(1, v));
    const cubic = (a, b, c, d, u) => {
        const v = 1 - u;
        return v * v * v * a + 3 * v * v * u * b + 3 * v * u * u * c + u * u * u * d;
    };
    function easing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let lo = 0, hi = 1;
        for (let i = 0; i < 19; i++) {
            const m = (lo + hi) / 2;
            if (cubic(0, x1, x2, 1, m) < p)
                lo = m;
            else
                hi = m;
        }
        return cubic(0, y1, y2, 1, (lo + hi) / 2);
    }
    const fade = (a, b) => easing((t - a) / (b - a), .16, .35, .24, 1);
    const op = (id, v) => $(id).setAttribute('opacity', String(clamp(v)));
    const entrance = (id, a, b) => {
        const p = fade(a, b);
        op(id, p);
        $(id).setAttribute('transform', `translate(0 ${((1 - p) * 5).toFixed(2)})`);
    };
    function render() {
        const switchP = fade(1700, 2180);
        op('kr12start', 1 - switchP);
        op('kr12focus', switchP);
        $('kr12workText').textContent = t >= 930 ? 'Summarizing authorized risk categories...' : 'Organizing authorized insights...';
        $('kr12dots').querySelectorAll('circle').forEach((dot, i) => {
            dot.setAttribute('opacity', String(.30 + .70 * Math.sin(t / 260 - i * .8) ** 2));
        });
        entrance('kr12insight', 2170, 2600);
        entrance('kr12metric1', 2600, 3040);
        entrance('kr12metric2', 2840, 3280);
        entrance('kr12metric3', 3080, 3520);
        entrance('kr12actionTitle', 3560, 3880);
        entrance('kr12action1', 3900, 4330);
        entrance('kr12action2', 4250, 4680);
        entrance('kr12action3', 4600, 5030);
        const provenance = fade(5180, 5580);
        op('kr12footerInitial', 1 - provenance);
        op('kr12footerFinal', provenance);
    }
    return (time) => { t = time; render(); };
}
export function clip12(root) {
    const $ = id => root.querySelector('#' + id);
    let t = 0;
    const focused = 0;
    const clamp = x => Math.max(0, Math.min(1, x));
    const bez = (a, b, c, d, p) => { const q = 1 - p; return q * q * q * a + 3 * q * q * p * b + 3 * q * p * p * c + p * p * p * d; };
    function easing(p, x1 = .45, y1 = 0, x2 = .23, y2 = 1) {
        p = clamp(p);
        let lo = 0, hi = 1;
        for (let i = 0; i < 19; i++) {
            const m = (lo + hi) / 2;
            if (bez(0, x1, x2, 1, m) < p)
                lo = m;
            else
                hi = m;
        }
        return bez(0, y1, y2, 1, (lo + hi) / 2);
    }
    const motion = (a, b) => easing((t - a) / (b - a));
    const fade = (a, b) => easing((t - a) / (b - a), .14, .35, .24, 1);
    const op = (id, v) => $(id).setAttribute('opacity', String(clamp(v)));
    function pointer() {
        if (t < 410)
            return { x: 680, y: 410 };
        if (t < 1370) {
            const p = motion(410, 1370);
            return {
                x: bez(680, 587, 449, 362, p),
                y: bez(410, 419, 473, 474, p)
            };
        }
        return { x: 362, y: 474 };
    }
    function render() {
        const change = fade(2680, 3160);
        op('kr13v2start', 1 - change);
        op('kr13v2end', change);
        op('kr13v2footer0', 1 - change);
        op('kr13v2footer1', change);
        const hover = fade(1250, 1440) * (1 - fade(2010, 2180));
        op('kr13v2hover', hover);
        $('kr13v2weekBg').setAttribute('stroke', t >= 1430 && t < 2730 ? '#9db7cb' : '#4e555a');
        $('kr13v2hit').style.pointerEvents = t < 2210 ? 'auto' : 'none';
        const m = motion(2370, 3370);
        const morphOpacity = fade(2180, 2370) * (1 - fade(3290, 3650));
        op('kr13v2morph', morphOpacity);
        $('kr13v2morphRect').setAttribute('y', String(432 - 108 * m));
        $('kr13v2morphRect').setAttribute('height', String(94 + 107 * m));
        $('kr13v2morphRect').setAttribute('rx', String(8 + 2 * m));
        $('kr13v2morphText').setAttribute('transform', `translate(0 ${(-108 * m).toFixed(2)})`);
        op('kr13v2morphText', 1 - fade(2610, 2960));
        const line = motion(3400, 5270);
        $('kr13v2line').setAttribute('stroke-dashoffset', String(558 * (1 - line)));
        op('kr13v2nodes', fade(3440, 3840));
        for (const [id, a, b] of [
            ['kr13v2card1', 3460, 3810],
            ['kr13v2card2', 4050, 4460],
            ['kr13v2card3', 4650, 5060]
        ]) {
            const p = fade(a, b);
            op(id, p);
            $(id).setAttribute('transform', `translate(0 ${((1 - p) * 6).toFixed(2)})`);
        }
        for (let i = 1; i <= 3; i++) {
            const bg = $('kr13v2dest' + i);
            if (bg)
                bg.setAttribute('stroke', focused === i ? '#a5c6db' : i === 1 ? '#7896aa' : '#525e66');
        }
        const pos = pointer();
        $('kr13v2cursor').setAttribute('transform', `translate(${pos.x.toFixed(2)} ${pos.y.toFixed(2)})`);
        op('kr13v2cursor', 1 - fade(2470, 2750));
        if (t >= 2050 && t < 2250) {
            const p = clamp((t - 2050) / 200);
            $('kr13v2ripple').setAttribute('transform', 'translate(362 474)');
            $('kr13v2ripple').querySelector('circle').setAttribute('r', String(9 + 17 * p));
            op('kr13v2ripple', (1 - p) * .7);
        }
        else
            op('kr13v2ripple', 0);
    }
    return (time) => { t = time; render(); };
}
