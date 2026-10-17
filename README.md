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
  - **入力柔軟性**: Gazeboシミュレータ上のカメラ映像からのリアルタイム自動認識に加え、テストコマンドによる仮想トピック配信（トリガーコマンド）の双方からシームレスに動作・検証が可能
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
```

---

## 🚀 セットアップおよび動作確認手順

### Step 1: リポジトリのクローンとビルド

ワークスペースの `src` ディレクトリにクローンし、パッケージをビルドします。

```bash
# ROS 2 ワークスペースの src ディレクトリへ移動
cd ~/pai_ws/src

# リポジトリのクローン
git clone https://github.com/ToshiyukiSano/PhysicalAI2026_Practical1_FinalAssignment.git

# ワークスペース直下に戻りビルドとセットアップファイルの読み込み
cd ~/pai_ws
colcon build --symlink-install --packages-select physicalai_pubsub
source install/setup.bash
```

### Step 2: シミュレータ（Gazebo）の起動

**【ターミナル 1】** CRANE+ V2 の Gazebo シミュレーション環境を立ち上げます。

```bash
source ~/pai_ws/install/setup.bash
ros2 launch crane_plus_gazebo crane_plus_with_table.launch.py
```

### Step 3: 制御ノード（action_publisher）の起動

**【ターミナル 2】** 新しいターミナルを開き、実装した色判定・アクション制御ノードを起動します。

```bash
source ~/pai_ws/install/setup.bash
ros2 run physicalai_pubsub action_publisher
```

### Step 4: 動作確認（カメラ認識 または トリガーコマンド）

本ノードは**「カメラ映像からの自動応答」**と**「トリガーコマンドによる手動検証」**のどちらからでも動作させることができます。

#### ① Gazebo上のカメラ画像による動作確認
Gazeboシミュレータ内でカメラの視界に赤色または青色のオブジェクトを配置すると、リアルタイムに色を判別して対応するモーションが実行されます。

#### ② トリガーコマンド（仮想カラー信号）による動作確認
**【ターミナル 3】** 以下のコマンドを実行して擬似的なカラー画像をトピックに直接パブリッシュし、各動作を即座に検証・再現できます。

- **赤色トリガーコマンド（横振りウェーブ動作：約20秒間）**
  ```bash
  source ~/pai_ws/install/setup.bash
  python3 -c "import rclpy, cv2, numpy as np; from cv_bridge import CvBridge; from sensor_msgs.msg import Image; rclpy.init(); node = rclpy.create_node('test_pub'); pub = node.create_publisher(Image, '/camera/image_raw', 10); img = np.full((100,100,3), (0,0,255), dtype=np.uint8); msg = CvBridge().cv2_to_imgmsg(img, encoding='bgr8'); pub.publish(msg); print('Sent RED test image'); rclpy.shutdown()"
  ```

- **青色トリガーコマンド（上下お辞儀動作：約20秒間）**
  ```bash
  source ~/pai_ws/install/setup.bash
  python3 -c "import rclpy, cv2, numpy as np; from cv_bridge import CvBridge; from sensor_msgs.msg import Image; rclpy.init(); node = rclpy.create_node('test_pub'); pub = node.create_publisher(Image, '/camera/image_raw', 10); img = np.full((100,100,3), (255,0,0), dtype=np.uint8); msg = CvBridge().cv2_to_imgmsg(img, encoding='bgr8'); pub.publish(msg); print('Sent BLUE test image'); rclpy.shutdown()"
  ```
