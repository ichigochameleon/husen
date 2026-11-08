import {
  BrowserRouter,
  Routes,
  Route,
  Link,
  Navigate,
  useParams,
  useLocation,
} from "react-router-dom";
import React, {useEffect, useState} from "react";
import {projects} from "./mock.js";
import {memo} from "./mock.js";


function Layout({ children }) {
  const location = useLocation();

  const isProjectPage =
    location.pathname.startsWith("/projects/");

  return (
    <div className="drawer lg:drawer-open">
      <input
        id="my-drawer-4"
        type="checkbox"
        className="drawer-toggle"
      />

      <div className="drawer-content">
        {/* Navbar */}
        <nav className="navbar w-full bg-base-300">
          <label
            htmlFor="my-drawer-4"
            aria-label="open sidebar"
            className="btn btn-square btn-ghost drawer-button"
          >
            {/* ここは元のSVG */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              strokeLinejoin="round"
              strokeLinecap="round"
              strokeWidth="2"
              fill="none"
              stroke="currentColor"
              className="my-1.5 inline-block size-4"
            >
              <path d="M4 4m0 2a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-12a2 2 0 0 1-2-2z" />
              <path d="M9 4v16" />
              <path d="M14 10l2 2l-2 2" />
            </svg>
          </label>

          {/* ここだけ変更 */}
          <div className="px-4">
            {isProjectPage ? "プロジェクト" : "ホーム"}
          </div>
        </nav>

        {children}
      </div>

      {/* Sidebar */}
      <div className="drawer-side is-drawer-close:overflow-visible">
        <label
          htmlFor="my-drawer-4"
          aria-label="close sidebar"
          className="drawer-overlay"
        />

        <div className="flex min-h-full flex-col items-start bg-base-200 is-drawer-close:w-14 is-drawer-open:w-64">
          <ul className="menu h-full w-full grow flex flex-col">

            {/* Home */}
            <li>
              <Link
                to="/"
                className="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                data-tip="Homepage"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  strokeLinejoin="round"
                  strokeLinecap="round"
                  strokeWidth="2"
                  fill="none"
                  stroke="currentColor"
                  className="my-1.5 inline-block size-4"
                >
                  <path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8" />
                  <path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
                </svg>

                <span className="is-drawer-close:hidden">
                  Homepage
                </span>
              </Link>
            </li>

            {/* Settings */}
            <li className="mt-auto">
              <button
                className="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                data-tip="Settings"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 24 24"
                  strokeLinejoin="round"
                  strokeLinecap="round"
                  strokeWidth="2"
                  fill="none"
                  stroke="currentColor"
                  className="my-1.5 inline-block size-4"
                >
                  <path d="M20 7h-9" />
                  <path d="M14 17H5" />
                  <circle cx="17" cy="17" r="3" />
                  <circle cx="7" cy="7" r="3" />
                </svg>

                <span className="is-drawer-close:hidden">
                  Settings
                </span>
              </button>
            </li>

            {/* User */}
            <li>
              <button
                className="is-drawer-close:tooltip is-drawer-close:tooltip-right"
                data-tip="YOURNAME"
              >
                <div className="avatar shrink-0">
                  <div className="size-5 rounded-full">
                    <img
                      alt="avatar"
                      src="https://img.daisyui.com/images/profile/demo/yellingcat@192.webp"
                    />
                  </div>
                </div>

                <span className="is-drawer-close:hidden">
                  YOURNAME
                </span>
              </button>
            </li>

          </ul>
        </div>
      </div>
    </div>
  );
}

/* =========================
   ホーム
========================= */

function Home() {
  const [loading,setLoading]=useState(true);
  const [error,setError]=useState(null);

  const [serverUrl,setServerUrl]=useState('http://127.0.0.1:8000');
  const [projects,setProjects]=useState([]);



  const [text,setText]=useState('');

  const send_text=async (name)=> {

    setError(null);
    try {
      const res = await fetch(serverUrl + "/" + "projects/", {
        method: 'post',
        headers: {'Content-Type': 'application/json',},
        body: JSON.stringify({
          name,
        })
      });
      if (!res.ok) {
        throw new Error(`HTTP ${res.status} ${res.statusText}`);
      }
      const data = await res.json();
      setProjects((currentProjects) => [...currentProjects, data]);
      setText('');
    } catch (e) {
      if (e instanceof DOMException && e.name === 'AbortError') return;
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const handlekeydown=(e)=>{
    if (e.key === 'Enter' && !e.nativeEvent.isComposing){
      if (!e.shiftKey){
        e.preventDefault();
        const textData=e.currentTarget.value;

        if (textData.trim() === '') return;
        send_text(textData.trim());

      }

    }
  }

  useEffect(()=>{
    setLoading(true);
    setError(null);
    async function load(){
    try{
      const res=await fetch(serverUrl+"/"+"projects/");
      if (!res.ok){
        throw new Error(`HTTP ${res.status} ${res.statusText}`);
      }
      const data=await res.json();
      setProjects(data);
      setLoading(false);
    } catch (e){
      if (e instanceof  DOMException && e.name ==='AbortError') return;
      setError(e instanceof  Error ? e.message:String(e));
      setLoading(false);
    }}
    load();
  },[])
  return (
    <main>
      {/* Search */}
      <div className="p-4">
        <div className="join w-full">

          <div className="grow">
            <input
              className="input join-item w-full"
              placeholder="プロジェクトを検索"
            />
          </div>

          <select className="select join-item" defaultValue="">
            <option value="" disabled>
              Filter
            </option>
            <option>結論</option>
            <option>途中経過</option>
            <option>未結論</option>
          </select>

          <button className="btn join-item">
            検索
          </button>

        </div>
      </div>

      {/* Projects */}
      <div className="px-4 pb-8">
        <h1 className="mb-4 text-2xl font-bold">
          プロジェクト
        </h1>

        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          {projects.map((project) => (
            <Link
              key={project.id}
              to={`/projects/${project.id}`}
              className="card bg-base-200 shadow-sm transition hover:shadow-md"
            >
              <div className="card-body">

                <h2 className="card-title">
                  {project.name}
                </h2>

                <p className="text-base-content/70">
                  {project.overview}
                </p>

                {/* Status */}
                <div className="mt-4 flex gap-5">

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="結論"
                      className="status status-success"
                    />
                    <span>{project.conclusion}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="途中経過"
                      className="status status-warning"
                    />
                    <span>{project.progress}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="未結論"
                      className="status status-error"
                    />
                    <span>{project.unresolved}</span>
                  </div>

                </div>

              </div>
            </Link>
          ))}

        </div>
        <textarea className="textarea textarea-bordered fixed bottom-4 right-4 z-50 w-64 h-24 shadow-lg"  placeholder="新しいプロジェクト" value={text} onKeyDown={handlekeydown} onChange={(e)=>setText(e.target.value)}></textarea>
      </div>
    </main>
  );
}


/* =========================
   プロジェクト詳細
========================= */

function ProjectDetail() {
  const { id } = useParams();
  console.log(id);
  const project = projects.find(
    (project) => project.id === Number(id)
  );

  if (!project) {
    return (
      <main className="p-4">
        <h1 className="text-2xl font-bold">
          プロジェクトが見つかりません
        </h1>
      </main>
    );
  }

  const projectmemos=memo.filter((item)=>item.project_id=project.id);
  const unresolve_projectmemos=projectmemos.filter((item)=>item.progress=0);
  const progress_projectmemos=projectmemos.filter((item)=>item.progress=1);
  const complete_projectmemos=projectmemos.filter((item)=>item.progress=2);


  return (
    <main className="p-4">
      <h1 className="text-2xl font-bold">
        {project.name}
      </h1>
      <div className="flex w-full">

        <details className="collapse collapse-arrow bg-base-100 border border-base-300" name="overview-accordion">
        <summary className="collapse-title font-semibold">概要</summary>
        <div className="collapse-content text-sm">{project.overview}</div>
        </details>

        <div className="divider divider-horizontal"></div>

        <details className="collapse collapse-arrow bg-base-100 border border-base-300" name="url-accordion">
        <summary className="collapse-title font-semibold">URL</summary>
        <div className="collapse-content text-sm">{project.mainchat_url}</div>
        </details>

      </div>
      <div className="p-4">
        <div className="join w-full">

          <div className="grow">
            <input
              className="input join-item w-full"
              placeholder="メモを検索"
            />
          </div>

          <select className="select join-item" defaultValue="">
            <option value="" disabled>
              Filter
            </option>
            <option>結論</option>
            <option>途中経過</option>
            <option>未結論</option>
          </select>

          <button className="btn join-item">
            検索
          </button>
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

          {memo.map((memo) => (
            <Link
              key={memo.id}
              to={`/projects/${project.id}`}
              className="card bg-base-200 shadow-sm transition hover:shadow-md"
            >
              <div className="card-body">

                <h2 className="card-title">
                  {pr.name}
                </h2>

                <p className="text-base-content/70">
                  {project.overview}
                </p>

                {/* Status */}
                <div className="mt-4 flex gap-5">

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="結論"
                      className="status status-success"
                    />
                    <span>{project.conclusion}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="途中経過"
                      className="status status-warning"
                    />
                    <span>{project.progress}</span>
                  </div>

                  <div className="flex items-center gap-2">
                    <div
                      aria-label="未結論"
                      className="status status-error"
                    />
                    <span>{project.unresolved}</span>
                  </div>

                </div>

              </div>
            </Link>
          ))}

        </div>
        </div>
      </div>
      {unresolve_projectmemos.map((item) => (
              <div
                key={item.id}
                className="card bg-base-200 shadow-sm"
              >
                <div className="card-body p-4">

                  <h3 className="font-bold">
                    {item.name}
                  </h3>

                  <p className="text-sm">
                    {item.text}
                  </p>

                  <div className="badge badge-outline">
                    {item.kinds}
                  </div>

                </div>
              </div>
            ))}
    </main>
  );
}




/* =========================
   App
========================= */

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/projects/" replace />} />
          <Route path="/projects/" element={<Home />} />
          <Route path="/projects/:id" element={<ProjectDetail />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;