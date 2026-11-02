import { readFileSync } from 'node:fs';
import { render } from '@testing-library/react';
import { expect,it } from 'vitest';
import { SignalV4 } from '../src/features/marketing/signal-v4';
import { signalMarkup } from '../src/features/marketing/signal-v4-source';

it('preserves the exact founder AppBlock, its source CSS, and native vector geometry',()=>{
 const source=readFileSync('../../docs/m8/pr7/signal-integration/signal-source/KryptRoom_The_Signal_V4.html','utf8');
 expect(signalMarkup).toBe(source.slice(source.indexOf('<div id="kr-signal-v4"'),source.lastIndexOf('</div>')+6));
 const {container}=render(<SignalV4/>);
 const native=document.createElement('div');native.innerHTML=signalMarkup;
 function tree(e:Element):unknown{return {tag:e.tagName,attrs:[...e.attributes].map(a=>[a.name,a.value]).sort(),text:e.children.length?'':e.textContent,children:[...e.children].map(tree)};}
 expect(tree(container.querySelector('svg')!)).toEqual(tree(native.querySelector('svg')!));
 expect(container.querySelector('style')?.textContent).toBe(native.querySelector('style')?.textContent);
 expect(container.querySelector('svg')).toHaveAttribute('viewBox','0 0 1000 508');
 expect([...container.querySelectorAll('.rings circle')].map(e=>[e.getAttribute('cx'),e.getAttribute('cy'),e.getAttribute('r')])).toEqual([['370','300','55'],['430','300','55']]);
 expect([...container.querySelectorAll('.risk-fill-group rect')].map(e=>e.getAttribute('width'))).toEqual(['173','115.33','57.67']);
 expect(container.querySelectorAll('button,video,canvas,img,iframe,script')).toHaveLength(0);
});
