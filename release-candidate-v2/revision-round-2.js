(function () {
  'use strict';
  function qs(selector) { return document.querySelector(selector); }
  function value(id) { var node = qs('#' + id); return node ? node.value.trim() : ''; }
  function setValue(id, text) { var node = qs('#' + id); if (node) node.value = text || ''; }
  function status(id, text) { var node = qs('#' + id); if (node) node.textContent = text; }
  function save(key, object) { try { localStorage.setItem(key, JSON.stringify(object)); return true; } catch (err) { return false; } }
  function load(key) { try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch (err) { return null; } }
  function remove(key) { try { localStorage.removeItem(key); } catch (err) {} }

  function updateReadingUI() {
    var scrollRoot = document.scrollingElement || document.documentElement;
    var top = scrollRoot.scrollTop || window.pageYOffset || 0;
    var height = Math.max(1, scrollRoot.scrollHeight - scrollRoot.clientHeight);
    var percent = Math.max(0, Math.min(100, top / height * 100));
    var progress = qs('.sc-reading-progress');
    var bar = qs('.sc-reading-progress-bar');
    if (bar) {
      bar.style.width = '100%';
      bar.style.transform = 'scaleX(' + (percent / 100) + ')';
    }
    if (progress) progress.setAttribute('aria-valuenow', String(Math.round(percent)));
    document.documentElement.style.setProperty('--sc-progress-hue', String(Math.round(210 - percent * .9)));
    var header = qs('.header');
    var sticky = qs('.sc-sticky-chapter');
    if (header && sticky) {
      sticky.classList.toggle('is-visible', header.getBoundingClientRect().bottom < 58 && top < height - 40);
    }
  }

  function initQuoteTool() {
    var button = qs('#scBuildQuote');
    if (!button) return;
    var key = 'scholarsCompass:chapter-4:prepare-present-explain';
    function data() { return { point:value('scQuotePoint'), context:value('scQuoteContext'), evidence:value('scQuoteEvidence'), explanation:value('scQuoteExplanation') }; }
    function render() { var d=data(); status('scQuoteOutput', [d.point,d.context,d.evidence,d.explanation].filter(Boolean).join(' ')); }
    button.addEventListener('click', render);
    qs('#scSaveQuote').addEventListener('click', function(){ save(key,data()); status('scQuoteOutput','Saved in this browser.'); });
    qs('#scClearQuote').addEventListener('click', function(){ ['scQuotePoint','scQuoteContext','scQuoteEvidence','scQuoteExplanation'].forEach(function(id){setValue(id,'');}); remove(key); status('scQuoteOutput','Cleared.'); });
    var stored=load(key); if(stored){ Object.keys(stored).forEach(function(name){ var ids={point:'scQuotePoint',context:'scQuoteContext',evidence:'scQuoteEvidence',explanation:'scQuoteExplanation'}; setValue(ids[name],stored[name]); }); }
  }

  function initRhetoricTool() {
    var button=qs('#scBuildRhetoric'); if(!button) return;
    button.addEventListener('click', function(){
      var parts=[['Choice',value('scRhetChoice')],['Effect',value('scRhetEffect')],['Audience',value('scRhetAudience')],['Purpose',value('scRhetPurpose')]];
      status('scRhetoricOutput',parts.filter(function(p){return p[1];}).map(function(p){return p[0]+': '+p[1];}).join('\n'));
    });
    qs('#scClearRhetoric').addEventListener('click',function(){['scRhetChoice','scRhetEffect','scRhetAudience','scRhetPurpose'].forEach(function(id){setValue(id,'');}); status('scRhetoricOutput','Cleared.');});
  }

  function initAnalysisTool() {
    var button=qs('#scBuildAnalysis'); if(!button) return;
    var key='scholarsCompass:chapter-10:observation-interpretation-significance';
    function data(){return {observation:value('scAnalysisObservation'),interpretation:value('scAnalysisInterpretation'),significance:value('scAnalysisSignificance')};}
    function render(){var d=data();status('scAnalysisOutput',['Observation: '+d.observation,'Interpretation: '+d.interpretation,'Significance: '+d.significance].join('\n'));}
    button.addEventListener('click',render);
    qs('#scSaveAnalysis').addEventListener('click',function(){save(key,data());status('scAnalysisOutput','Saved in this browser.');});
    qs('#scClearAnalysis').addEventListener('click',function(){['scAnalysisObservation','scAnalysisInterpretation','scAnalysisSignificance'].forEach(function(id){setValue(id,'');});remove(key);status('scAnalysisOutput','Cleared.');});
    var d=load(key); if(d){setValue('scAnalysisObservation',d.observation);setValue('scAnalysisInterpretation',d.interpretation);setValue('scAnalysisSignificance',d.significance);}
  }

  function initSynthesisTool() {
    var saveButton=qs('#scSaveSynthesis'); if(!saveButton) return;
    var key='scholarsCompass:chapter-13:synthesis-planner';
    var fields=['scSynthClaim','scSynthA','scSynthB','scSynthRelationship','scSynthConclusion','scSynthMissing'];
    function data(){var d={};fields.forEach(function(id){d[id]=value(id);});return d;}
    function restore(d){if(!d)return;fields.forEach(function(id){setValue(id,d[id]);});}
    saveButton.addEventListener('click',function(){status('scSynthesisStatus',save(key,data())?'Synthesis notes saved in this browser.':'The notes could not be saved in this browser.');});
    qs('#scLoadSynthesis').addEventListener('click',function(){var d=load(key);restore(d);status('scSynthesisStatus',d?'Saved notes loaded.':'No saved synthesis notes were found.');});
    qs('#scClearSynthesis').addEventListener('click',function(){fields.forEach(function(id){setValue(id,'');});remove(key);status('scSynthesisStatus','Synthesis notes cleared.');});
    restore(load(key));
  }

  function ready() {
    updateReadingUI();
    var ticking=false;
    window.addEventListener('scroll',function(){if(ticking)return;ticking=true;requestAnimationFrame(function(){updateReadingUI();ticking=false;});},{passive:true});
    window.addEventListener('resize',updateReadingUI,{passive:true});
    window.addEventListener('load',updateReadingUI,{once:true});
    window.addEventListener('pageshow',updateReadingUI);
    setTimeout(updateReadingUI, 100);
    initQuoteTool(); initRhetoricTool(); initAnalysisTool(); initSynthesisTool();
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',ready);else ready();
})();
