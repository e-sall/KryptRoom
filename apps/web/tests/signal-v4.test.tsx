import { readFileSync } from 'node:fs';
import { render } from '@testing-library/react';
import { expect,it } from 'vitest';
import { SignalV4 } from '../src/features/marketing/signal-v4';
import { signalMarkup } from '../src/features/marketing/signal-v4-source';

it('preserves the founder source, CSS and vector geometry except the approved footer removal',()=>{
 const source=readFileSync('../../docs/m8/pr7/signal-integration/signal-source/KryptRoom_The_Signal_V4.html','utf8');
 expect(signalMarkup).toBe(source.slice(source.indexOf('<div id="kr-signal-v4"'),source.lastIndexOf('</div>')+6));
 const {container}=render(<SignalV4/>);
 const native=document.createElement('div');native.innerHTML=signalMarkup;
 const footer=[...native.querySelectorAll('svg text')].find(e=>e.textContent==='SYNTHETIC PREVIEW · NO LIVE COMPUTATION');
 expect(footer).toBeDefined();
 footer!.remove();
 function tree(e:Element):unknown{return {tag:e.tagName,attrs:[...e.attributes].map(a=>[a.name,a.value]).sort(),text:e.children.length?'':e.textContent,children:[...e.children].map(tree)};}
 expect(tree(container.querySelector('svg')!)).toEqual(tree(native.querySelector('svg')!));
 expect(container.querySelector('style')?.textContent).toBe(native.querySelector('style')?.textContent);
 expect(container.querySelector('svg')).toHaveAttribute('viewBox','0 0 1000 508');
 expect([...container.querySelectorAll('.rings circle')].map(e=>[e.getAttribute('cx'),e.getAttribute('cy'),e.getAttribute('r')])).toEqual([['370','300','55'],['430','300','55']]);
 expect([...container.querySelectorAll('.risk-fill-group rect')].map(e=>e.getAttribute('width'))).toEqual(['173','115.33','57.67']);
 expect(container.querySelectorAll('button,video,canvas,img,iframe,script')).toHaveLength(0);
 const links=container.querySelectorAll<HTMLAnchorElement>('.signal-walkthrough-link');
 expect(links).toHaveLength(1);
 expect(links[0]).toHaveAttribute('href','/demo#product-walkthrough');
 expect(links[0].textContent).toBe('Explore the full product walkthrough →');
 expect(container.querySelector('.signal-art')).toContainElement(links[0]);
 expect(container.querySelector('.signal-followup')).toBeNull();
 expect(container.textContent).not.toMatch(/synthetic preview · no live computation/i);
});
