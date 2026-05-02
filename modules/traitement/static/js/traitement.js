let editor;

window.onload = function(){

editor = ace.edit("editor");
editor.setTheme("ace/theme/monokai");
editor.session.setMode("ace/mode/python");

chargerSourcesLac();
chargerSourcesClean();

};


function chargerSourcesLac(){

fetch("/traitement/api/sources-lac")
.then(r=>r.json())
.then(data=>{

let tbody = document.querySelector("#table_lac tbody");
tbody.innerHTML="";

data.forEach(row=>{

let tr=document.createElement("tr");

tr.innerHTML=`
<td>${row.id}</td>
<td>${row.intitule_source}</td>
<td>${row.nom_fichier}</td>
<td>${row.annee}</td>
<td>${row.mois}</td>
<td>${row.type_personne}</td>
<td>${row.date_stockage}</td>
`;

tbody.appendChild(tr);

});

});

}


function chargerSourcesClean(){

fetch("/traitement/api/sources-clean")
.then(r=>r.json())
.then(data=>{

let tbody=document.querySelector("#table_clean tbody");
tbody.innerHTML="";

data.forEach(row=>{

let tr=document.createElement("tr");

tr.innerHTML=`
<td>${row.id}</td>
<td>${row.intitule_source}</td>
<td>
<a href="/traitement/tableur/${row.nom_fichier}" target="_blank">
${row.nom_fichier}
</a>
</td>
<td>${row.annee}</td>
<td>${row.mois}</td>
<td>${row.type_personne}</td>
<td>${row.date_stockage}</td>
`;

tbody.appendChild(tr);

});

});

}


function executer(){

let script = editor.getValue();

let source_id = prompt("Entrer ID de la source LAC");

fetch("/traitement/api/execute",{

method:"POST",
headers:{'Content-Type':'application/json'},

body:JSON.stringify({
source_id:source_id,
script:script
})

})
.then(r=>r.json())
.then(res=>{

alert(res.stdout || res.stderr);

chargerSourcesClean();

});

}