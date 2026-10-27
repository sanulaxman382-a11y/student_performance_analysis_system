const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];
let branches = [], students = [], subjects = [], assessments = [], results = [], marks = [], chart;
const esc = (v) => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
async function api(path, options={}) {
  const response = await fetch(path, {headers:{'Content-Type':'application/json'}, ...options});
  const body = await response.json().catch(()=>({}));
  if (!response.ok) throw new Error(body.error || body.message || `Request failed (${response.status})`);
  return body;
}
function notify(message, error=false) {
  const el=$('#notice'); el.textContent=message; el.classList.toggle('error',error); el.classList.remove('hidden');
  window.scrollTo({top:0,behavior:'smooth'}); setTimeout(()=>el.classList.add('hidden'),4500);
}
function formData(form){return Object.fromEntries(new FormData(form).entries())}
function options(el, rows, label, placeholder='Select an option') {
  el.innerHTML = `<option value="">${esc(placeholder)}</option>` + rows.map(r=>`<option value="${r.id}">${esc(label(r))}</option>`).join('');
}
function showPage(name){
  $$('.page').forEach(p=>p.classList.toggle('hidden',p.id!==`page-${name}`));
  $$('.nav-link').forEach(b=>b.classList.toggle('active',b.dataset.page===name));
  const titles={dashboard:'Dashboard',students:'Student management',branches:'Branch management',subjects:'Subject management',assessments:'Assessment management',marks:'Marks entry',results:'Results & reports'};
  $('#page-title').textContent=titles[name]||'Dashboard';
  if(name==='results') loadReports();
}
$$('.nav-link').forEach(b=>b.addEventListener('click',()=>showPage(b.dataset.page)));
$$('[data-goto]').forEach(b=>b.addEventListener('click',()=>showPage(b.dataset.goto)));
async function loadBranches(){
  branches=await api('/api/branches');
  $('#branches-table').innerHTML=branches.map(b=>`<tr><td>${b.id}</td><td class="student-name">${esc(b.name)}</td></tr>`).join('')||'<tr><td colspan="2">No branches yet.</td></tr>';
  options($('#student-branch'),branches,b=>b.name);
  $('#subject-branch').innerHTML='<option value="">All branches / common</option>'+branches.map(b=>`<option value="${b.id}">${esc(b.name)}</option>`).join('');
}
async function loadStudents(){
  students=await api('/api/students');
  $('#students-table').innerHTML=students.map(s=>`<tr><td>${esc(s.roll_no)}</td><td class="student-name">${esc(s.name)}</td><td>${esc(s.branch_name)}</td><td>${s.semester}</td><td><button class="text-btn" data-delete-student="${s.id}">Delete</button></td></tr>`).join('')||'<tr><td colspan="5">No students yet.</td></tr>';
  options($('#marks-student'),students,s=>`${s.roll_no} — ${s.name}`);
}
async function loadSubjects(){
  subjects=await api('/api/subjects');
  $('#subjects-table').innerHTML=subjects.map(s=>`<tr><td>${esc(s.code)}</td><td class="student-name">${esc(s.name)}</td><td>${esc(s.branch_name||'Common')}</td></tr>`).join('')||'<tr><td colspan="3">No subjects yet.</td></tr>';
  options($('#assessment-subject'),subjects,s=>`${s.code} — ${s.name}`);
}
async function loadAssessments(){
  assessments=await api('/api/assessments');
  $('#assessments-table').innerHTML=assessments.map(a=>`<tr><td class="student-name">${esc(a.title)}</td><td>${esc(a.subject_name)}</td><td>${a.semester}</td><td>${a.max_marks}</td><td>${esc(a.exam_date||'—')}</td></tr>`).join('')||'<tr><td colspan="5">No assessments yet.</td></tr>';
  options($('#marks-assessment'),assessments,a=>`${a.title} — ${a.subject_name} (max ${a.max_marks})`);
}
async function loadMarks(){
  marks=await api('/api/marks');
  $('#marks-table').innerHTML=marks.map(m=>`<tr><td>${esc(m.roll_no)}</td><td class="student-name">${esc(m.student_name)}</td><td>${esc(m.assessment_title)}</td><td>${m.marks_obtained} / ${m.max_marks}</td><td>${m.percentage}%</td></tr>`).join('')||'<tr><td colspan="5">No marks entered yet.</td></tr>';
}
function grade(p){return p>=90?'A+':p>=80?'A':p>=70?'B':p>=60?'C':p>=50?'D':p>=40?'E':'F'}
function resultRow(r){
 const status=r.percentage>=40?'Pass':'Needs support';
 return `<tr><td>${esc(r.roll_no)}</td><td class="student-name">${esc(r.name)}<span class="subtext">${esc(r.student_id)}</span></td><td>${esc(r.branch)} / Sem ${r.semester}</td><td>${esc(r.assessment)}<span class="subtext">${esc(r.subject)}</span></td><td>${r.percentage}%</td><td><span class="grade">${esc(r.grade||grade(r.percentage))}</span></td><td><span class="status ${status==='Pass'?'':'support'}">${status}</span></td></tr>`;
}
async function loadResults(){
 results=await api('/api/results');
 $('#results-table').innerHTML=results.map(resultRow).join('')||'<tr><td colspan="7">No results available. Create an assessment and enter marks.</td></tr>';
 $('#recent-results').innerHTML=results.slice(0,5).map(r=>`<tr><td class="student-name">${esc(r.name)}<span class="subtext">${esc(r.roll_no)}</span></td><td>${esc(r.assessment)}<span class="subtext">${esc(r.subject)}</span></td><td>${r.percentage}%</td><td><span class="grade">${esc(r.grade)}</span></td><td><span class="status ${r.percentage>=40?'':'support'}">${r.percentage>=40?'Pass':'Needs support'}</span></td></tr>`).join('')||'<tr><td colspan="5">No results available yet.</td></tr>';
}
async function loadDashboard(){
 const d=await api('/api/dashboard');
 $('#stat-students').textContent=d.students;$('#stat-branches').textContent=d.branches;$('#stat-subjects').textContent=d.subjects;
 $('#stat-average').innerHTML=`${d.class_average}<em>%</em>`;$('#stat-pass').textContent=`${d.pass_percentage}%`;
 $('#stat-support').textContent=d.assessed_records-Math.round(d.assessed_records*d.pass_percentage/100);
 $('#stat-assessments').textContent=d.assessments;
 if(chart) chart.destroy();
 chart=new Chart($('#performanceChart'),{type:'bar',data:{labels:['Class average','Pass rate'],datasets:[{label:'Percentage',data:[d.class_average,d.pass_percentage],backgroundColor:['#7769e8','#5cc5a0'],borderRadius:8,maxBarThickness:46}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},scales:{y:{beginAtZero:true,max:100,grid:{color:'#f0f1f7'},ticks:{callback:v=>v+'%'}},x:{grid:{display:false}}}}});
}
async function loadReports(){
 await loadResults();
 const avg=results.length?results.reduce((a,r)=>a+r.percentage,0)/results.length:0;
 const pass=results.length?results.filter(r=>r.percentage>=40).length/results.length*100:0;
 $('#report-average').textContent=avg.toFixed(2)+'%';$('#report-pass').textContent=pass.toFixed(2)+'%';
 $('#report-count').textContent=results.length;$('#report-support').textContent=results.filter(r=>r.percentage<40).length;
 const groups=await api('/api/reports/branches');
 $('#branch-report-table').innerHTML=groups.map(g=>`<tr><td class="student-name">${esc(g.branch)}</td><td>${g.semester}</td><td>${g.students}</td><td>${g.average_percentage==null?'—':g.average_percentage+'%'}</td><td>${g.pass_percentage==null?'—':g.pass_percentage+'%'}</td></tr>`).join('')||'<tr><td colspan="5">No comparison data yet.</td></tr>';
}
async function refreshAll(){
 await loadBranches();await loadStudents();await loadSubjects();await loadAssessments();await loadMarks();await loadResults();await loadDashboard();
}
async function submitForm(id,path,after){
 $('#'+id).addEventListener('submit',async e=>{
  e.preventDefault();
  const form=e.currentTarget, data=formData(form);
  try{await api(path,{method:'POST',body:JSON.stringify(data)});form.reset();notify('Saved successfully.');await after();await loadDashboard();}
  catch(err){notify(err.message,true)}
 });
}
submitForm('branch-form','/api/branches',async()=>{await loadBranches();await loadStudents();});
submitForm('student-form','/api/students',async()=>{await loadStudents();await loadResults();});
submitForm('subject-form','/api/subjects',async()=>{await loadSubjects();});
submitForm('assessment-form','/api/assessments',async()=>{await loadAssessments();});
submitForm('marks-form','/api/marks',async()=>{await loadMarks();await loadResults();});
document.addEventListener('click',async e=>{
 const btn=e.target.closest('[data-delete-student]');if(!btn)return;
 if(!confirm('Delete this student and all of their marks?'))return;
 try{await api(`/api/students/${btn.dataset.deleteStudent}`,{method:'DELETE'});notify('Student deleted.');await loadStudents();await loadMarks();await loadResults();await loadDashboard();}
 catch(err){notify(err.message,true)}
});
$('#student-search').addEventListener('input',e=>filterRows('#students-table',e.target.value));
$('#results-search').addEventListener('input',e=>filterRows('#results-table',e.target.value));
function filterRows(table,query){const q=query.toLowerCase();$$(`${table} tr`).forEach(r=>r.classList.toggle('hidden',!r.textContent.toLowerCase().includes(q)))}
$('#export-results').addEventListener('click',()=>{
 if(!results.length){notify('There are no results to export.',true);return}
 const cols=['roll_no','name','branch','semester','assessment','subject','max_marks','marks_obtained','percentage','grade','status'];
 const rows=[cols.join(','),...results.map(r=>cols.map(k=>`"${String(k==='status'?(r.percentage>=40?'Pass':'Needs support'):(r[k]??'')).replace(/"/g,'""')}"`).join(','))];
 const blob=new Blob([rows.join('\r\n')],{type:'text/csv;charset=utf-8;'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='student-performance-results.csv';a.click();URL.revokeObjectURL(url);
});
refreshAll().catch(err=>notify(`Could not load data: ${err.message}. Check that MySQL is running and the database is configured.`,true));
