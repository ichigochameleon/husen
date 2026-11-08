export const projects = [
  {
    id: 1,
    name: "テスト文化祭案内システム",
    overview: "文化祭の教室・展示・待ち時間などを案内するWebアプリ",
    conclusion: 3,
    progress: 5,
    unresolved: 2,
    mainchat_url:"https://annnai"
  },
  {
    id: 2,
    name: "テスト文化祭案内システムロボット汎用基板",
    overview: "UART・CAN・PWMなどに対応したロボット向け汎用基板",
    conclusion: 1,
    progress: 7,
    unresolved: 3,
    mainchat_url:"https://annnai"
  },
  {
    id: 3,
    name: "テスト屋内分散案内ネットワーク",
    overview: "複数の案内ノードを利用した分散型の屋内案内システム",
    conclusion: 0,
    progress: 2,
    unresolved: 5,
    mainchat_url:"https://annnai"
  },
  {
    id: 4,
    name: "テストHusen",
    overview: "プロジェクト内の情報を付箋のように管理するWebアプリ",
    conclusion: 8,
    progress: 0,
    unresolved: 0,
    mainchat_url:"https://annnai"
  },
];

export const memo = [
  {
    id: 1,
    name: "案内方法について",
    kinds: "案",
    others_kinds: "",
    text: "案内板に方向を表示するか検討する",
    project_id: 1,
    progress: 1,
  },
  {
    id: 2,
    name: "通信方式",
    kinds: "技術",
    others_kinds: "",
    text: "micro:bit間の通信方式を検討中",
    project_id: 1,
    progress: 2,
  },
  {
    id: 3,
    name: "実証実験",
    kinds: "実験",
    others_kinds: "",
    text: "実際の校内で案内システムを試験する",
    project_id: 1,
    progress: 0,
  },
  {
    id: 4,
    name: "最終仕様",
    kinds: "結論",
    others_kinds: "",
    text: "システムの仕様を確定した",
    project_id: 1,
    progress: 3,
  },
];