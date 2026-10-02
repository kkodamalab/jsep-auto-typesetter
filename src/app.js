import { countCharacters, paginate } from './typesetter.js';

const manuscript = document.querySelector('#manuscript');
const charsPerLine = document.querySelector('#chars-per-line');
const linesPerPage = document.querySelector('#lines-per-page');
const preview = document.querySelector('#preview');

function render() {
  const chars = Number(charsPerLine.value);
  const lines = Number(linesPerPage.value);
  const pages = paginate(manuscript.value, chars, lines);

  document.querySelector('#character-count').textContent = `${countCharacters(manuscript.value).toLocaleString('ja-JP')} 字`;
  document.querySelector('#chars-output').value = chars;
  document.querySelector('#lines-output').value = lines;
  document.querySelector('#page-count').textContent = `${pages.length} ページ`;
  preview.replaceChildren(...pages.map((content, index) => {
    const page = document.createElement('article');
    page.className = 'page';
    page.style.setProperty('--chars', chars);
    page.style.setProperty('--lines', lines);
    const text = document.createElement('p');
    text.textContent = content || 'ここにプレビューが表示されます';
    if (!content) text.className = 'placeholder';
    const number = document.createElement('span');
    number.className = 'page-number';
    number.textContent = String(index + 1);
    page.append(text, number);
    return page;
  }));
}

[manuscript, charsPerLine, linesPerPage].forEach((element) => element.addEventListener('input', render));
document.querySelector('#print-button').addEventListener('click', () => window.print());
render();
