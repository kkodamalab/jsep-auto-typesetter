export function countCharacters(text) {
  return Array.from(text.replace(/\s/g, '')).length;
}

export function paginate(text, charsPerLine, linesPerPage) {
  const capacity = Math.max(1, charsPerLine * linesPerPage);
  const paragraphs = text.replace(/\r\n?/g, '\n').split('\n');
  const characters = [];

  paragraphs.forEach((paragraph, index) => {
    characters.push(...Array.from(paragraph));
    if (index < paragraphs.length - 1) characters.push('\n');
  });

  if (characters.length === 0) return [''];
  const pages = [];
  for (let index = 0; index < characters.length; index += capacity) {
    pages.push(characters.slice(index, index + capacity).join(''));
  }
  return pages;
}
