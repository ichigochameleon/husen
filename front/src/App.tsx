import './App.css'
import React, { useState, useEffect } from 'react';

function MyButton() {
  return (
    <button>I'm a button</button>
  );
}

function App() {
  type Project = {
    name: string;
    overview: string;
    mainchat_url: string;
    mainrepo_url: string;
  };
  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    // 非同期関数の定義
    const fetchProjectData = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/projects/1');
        const data = await response.json();
        setProject(data); // データをstateに保存
        if (project) {
          console.log(project.name);
        }
      } catch (error) {
        console.error('データの取得に失敗しました:', error);
      } finally {
        setLoading(false); // ローディング状態を解除
      }
    };
    fetchProjectData();
  }, []); // 空の配列を渡すことで、マウント時の1回だけ実行

  if (loading) return <div>読み込み中...</div>;
  return (
    <div>
      {project ? (
        <div>
          <h1>{project.name}</h1>
          <p>{project.overview}</p>
          <p>{project.mainchat_url}</p>
          <p>{project.mainrepo_url}</p>
          <p>検索</p>
          <p></p>
        </div>
      ) : (
        <h1>error</h1>
      )}

    </div>
  );
}

export default App
