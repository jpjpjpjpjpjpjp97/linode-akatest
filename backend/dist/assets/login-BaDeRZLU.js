import{r as i,j as e,a as c,c as d,R as p}from"./index-WIp4F9el.js";const u=async(a,s)=>{a.preventDefault();try{const t=await(await c.post("/api/v1/oauth2/token/",s,{headers:{"content-type":"application/x-www-form-urlencoded"}})).data;window.location.replace("/")}catch(o){console.log(o)}};function m(){const a={username:"",password:""},[s,o]=i.useState(a),[t,l]=i.useState(!1);return i.useEffect(()=>{},[]),e.jsx("div",{children:e.jsxs("form",{onSubmit:n=>u(n,s),children:[e.jsxs("div",{children:[e.jsx("label",{htmlFor:"login_username",children:"Username "}),e.jsx("input",{id:"login_username",name:"login_username",type:"text",value:s.username,onChange:n=>o(r=>({...r,username:n.target.value}))})]}),e.jsxs("div",{children:[e.jsx("label",{htmlFor:"login_password",children:"Password "}),e.jsx("input",{id:"login_password",name:"login_password",type:t?"text":"password",value:s.password,onChange:n=>o(r=>({...r,password:n.target.value}))}),"Show"," ",e.jsx("input",{type:"checkbox",onChange:()=>l(!t),checked:t})]}),e.jsx("input",{type:"submit",value:"Login"})]})})}d.createRoot(document.getElementById("root")).render(e.jsx(p.StrictMode,{children:e.jsx(m,{})}));
