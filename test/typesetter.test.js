import test from 'node:test';
import assert from 'node:assert/strict';
import { countCharacters, paginate } from '../src/typesetter.js';

test('空白を除いてUnicode文字を数える', () => {
  assert.equal(countCharacters('春 は\n🌸'), 3);
});

test('指定した文字数と行数でページを分割する', () => {
  assert.deepEqual(paginate('あいうえおかきくけこ', 2, 2), ['あいうえ', 'おかきく', 'けこ']);
});

test('空の原稿にも空ページを返す', () => {
  assert.deepEqual(paginate('', 20, 18), ['']);
});
