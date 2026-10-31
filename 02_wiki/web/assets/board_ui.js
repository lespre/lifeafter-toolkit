/* Keep existing board filters and data handlers; adapt only their container. */
(function(){
 const filters=document.getElementById('boardFilters');
 if(!filters)return;
 const narrow=window.matchMedia('(max-width:760px)');
 const sync=()=>{filters.open=!narrow.matches;};
 sync();
 narrow.addEventListener('change',sync);
})();
