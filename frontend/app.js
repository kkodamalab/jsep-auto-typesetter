const $ = (selector) => document.querySelector(selector);
let demoMode = location.hostname.endsWith('github.io');

function show(message, error = false) { const node = $('#notice'); node.hidden = !message; node.textContent = message; node.classList.toggle('error', error); }
function fill(data) { $('#title').value = data.title || ''; $('#authors').value = (data.authors || []).map(a => `${a.name} | ${a.affiliation || ''}`).join('\n'); $('#abstract').value = data.abstract || ''; $('#body').value = data.body_markdown || ''; $('#warnings').innerHTML = (data.warnings || []).map(w => `<p class="warning">⚠ ${escapeHtml(w)}</p>`).join(''); }
function escapeHtml(value) { const div = document.createElement('div'); div.textContent = value; return div.innerHTML; }
function payload() { return { manuscript: { title: $('#title').value, authors: $('#authors').value.split('\n').filter(Boolean).map(row => { const [name, ...rest] = row.split('|'); return {name:name.trim(), affiliation:rest.join('|').trim()}; }), abstract:$('#abstract').value, body_markdown:$('#body').value, bibliography:'', warnings:[] }, font_size:Number($('#font').value), margin_mm:Number($('#margin').value) }; }

async function loadDemo() { fill(await fetch('./demo.json').then(r => r.json())); show('架空の原稿を読み込みました。デモデータは自由に編集できます。'); }
$('#demo').addEventListener('click', loadDemo);
$('#file').addEventListener('change', async ({target}) => { if (!target.files[0]) return; if (demoMode) return show('GitHub Pagesはデモ専用です。Word変換にはDocker版を使用してください。', true); show('Pandocで原稿を解析しています…'); const form = new FormData(); form.append('file', target.files[0]); try { const response = await fetch('/api/extract', {method:'POST', body:form}); const data = await response.json(); if (!response.ok) throw new Error(data.detail); fill(data); show('抽出が完了しました。内容と警告を確認してください。'); } catch (error) { show(error.message || '抽出に失敗しました。', true); } });
$('#pdf').addEventListener('click', async () => { if (demoMode) return show('デモモードではPDFを生成しません。Docker版で実行してください。', true); show('PDFを組版しています…'); try { const response = await fetch('/api/pdf', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload())}); if (!response.ok) { const data=await response.json(); throw new Error(data.detail); } const link=document.createElement('a'); link.href=URL.createObjectURL(await response.blob()); link.download='jsep-manuscript.pdf'; link.click(); URL.revokeObjectURL(link.href); show('PDFを生成しました。'); } catch(error) { show(error.message || 'PDF生成に失敗しました。', true); } });

async function initialize() { if (!demoMode) { try { const health=await fetch('/api/health').then(r=>r.json()); demoMode=!health.conversion; } catch { demoMode=true; } } $('#mode').textContent=demoMode?'DEMO MODE':'CONVERTER ONLINE'; $('#file').disabled=demoMode; $('#pdf').disabled=demoMode; if (demoMode) await loadDemo(); }
initialize();
