# PhysicalAI2026_Practical1_FinalAssignment

東京大学 松尾・岩澤研究室「Physical AI応用1講座」の最終課題成果物リポジトリです。  
Gazeboシミュレータ上の CRANE+ V2 ロボットアームに対し、カメラ画像からOpenCVを用いた色判定（赤・青）を行い、それぞれ異なる20秒間の多段階シーケンス動作を実行するROS 2制御ノードを実装しました。

---

## 🔗 成果物リンク

- **GitHubリポジトリ**: https://github.com/ToshiyukiSano/PhysicalAI2026_Practical1_FinalAssignment
- **実演動画 (YouTube)**: https://youtu.be/0DtLnlQqnMM

---

## 🛠 パッケージ・機能概要

- **使用パッケージ**: `physicalai_pubsub`
- **実行ノード**: `action_publisher.py`
- **主な実装機能**:
  - `/camera/image_raw` トピックからカメラ画像を取得し、`cv_bridge` 経由でOpenCVのHSV色空間処理を実施
  - 赤色および青色の判定ピクセル数を算出し、判定フラグを動的に更新
  - **赤色検出時**: 台座回転（`crane_plus_joint1`）を中心とした**左右横振りウェーブ動作（約20秒間）**を実行
  - **青色検出時**: 各関節連動（`joint2`〜`joint4`）による**上下お辞儀・うなずき動作（約20秒間）**を実行

---

## 📁 ディレクトリ構成

```text
PhysicalAI2026_Practical1_FinalAssignment/
├── README.md
└── physicalai_pubsub/
    ├── package.xml
    ├── setup.py
    ├── setup.cfg
    └── physicalai_pubsub/
        ├── __init__.py
        └── action_publisher.py
