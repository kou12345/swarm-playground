import io
import os
import sys
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from swarm import Swarm, Agent
from openai import OpenAI
from dotenv import load_dotenv


# スクリプトの先頭に以下を追加
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8")

load_dotenv()

# Rich consoleの初期化
console = Console(force_terminal=True, force_interactive=False, color_system="auto")

# OpenAI クライアントの設定
token = os.environ.get("GITHUB_TOKEN")
endpoint = "https://models.inference.ai.azure.com"
model_name = "gpt-4o-mini"

openai_client = OpenAI(
    base_url=endpoint,
    api_key=token,
)

client = Swarm(client=openai_client)


# Agent transfer functions
def transfer_to_requirements_analyst():
    return requirements_analyst


def transfer_to_architect():
    return architect


def transfer_to_task_manager():
    return task_manager


def transfer_to_document_generator():
    return document_generator


def transfer_to_document_reviewer():
    return document_reviewer


# Requirements Analyst Agent
requirements_analyst = Agent(
    name="Requirements Analyst",
    instructions="""あなたは要件分析の専門家です。

    以下の観点からプロジェクトの要件を分析してください：
    1. ビジネス要件の明確化
       - プロジェクトの目的と期待される効果
       - 具体的な成功指標（KPI）の設定
    
    2. 機能要件と非機能要件の特定
       - コア機能の詳細な定義
       - セキュリティ要件（認証、暗号化、データ保護）
       - バックアップと監査ログ
       - ユーザーアクセス管理
       - パフォーマンス要件
    
    3. ステークホルダーの期待と制約条件の整理
       - 各ステークホルダーの役割と責任
       - 予算と時間の制約
       - 技術的な制約
    
    4. 要件の優先順位付け
       - Must-Have, Should-Have, Could-Have, Won't-Have
       - 段階的な実装計画
    
    特に注意すべき点：
    - 曖昧な要件については具体的な質問を投げかける
    - 要件間の依存関係を明確にする
    - 実現可能性の観点からの検証
    - 将来的な拡張性の考慮
    
    アーキテクトやタスクマネージャーと協力して、実装可能な要件定義を目指してください。""",
    functions=[transfer_to_architect, transfer_to_task_manager],
)

# System Architect Agent
architect = Agent(
    name="System Architect",
    instructions="""あなたはシステムアーキテクトです。

    以下の観点から設計提案を行ってください：
    1. 技術スタックの選定
       - 各技術選択の根拠
       - 代替案の検討
       - クラウドサービスの具体的な選定
    
    2. システム構成の設計
       - コンポーネント間の関係
       - マイクロサービス/モノリスの選択
       - インフラストラクチャの設計
    
    3. データフローの設計
       - データモデルの定義
       - APIインターフェースの設計
       - キャッシング戦略
    
    4. 非機能要件への対応方針
       - スケーラビリティ（オートスケーリング、負荷分散）
       - セキュリティ（認証、暗号化、アクセス制御）
       - 可用性（バックアップ、障害対策）
       - パフォーマンス最適化
    
    特に注意すべき点：
    - スケーラビリティとメンテナンス性
    - セキュリティ要件への対応
    - 既存システムとの統合
    - コスト効率の考慮
    - 将来的な拡張性
    
    要件アナリストとタスクマネージャーと協力して、実装可能なアーキテクチャを設計してください。""",
    functions=[transfer_to_requirements_analyst, transfer_to_task_manager],
)

# Task Manager Agent
task_manager = Agent(
    name="Task Manager",
    instructions="""あなたはタスク管理の専門家です。

    以下の観点からタスクの分解と管理を行ってください：
    1. 要件からの具体的なタスク分解
       - UI/UXの設計と実装
       - バックエンドAPIの開発
       - インフラストラクチャの構築
       - テストと品質保証
    
    2. タスクの依存関係の特定
       - 前提条件の明確化
       - クリティカルパスの特定
       - マイルストーンの設定
    
    3. 工数見積もりの提案
       - 各タスクの所要時間
       - バッファの考慮
       - リソース配分
    
    4. 優先順位付けとスケジューリング
       - フェーズごとの目標設定
       - リスクを考慮したスケジュール
       - チェックポイントの設定
    
    特に注意すべき点：
    - タスクの粒度は2-3日で完了可能な大きさに
    - クリティカルパスの特定
    - リスクの早期発見と対策
    - チーム規模に応じた適切な分担
    - レビューポイントの設定
    
    要件アナリストとアーキテクトと協力して、実行可能なタスク計画を作成してください。""",
    functions=[transfer_to_requirements_analyst, transfer_to_architect],
)

# Document Generator Agent
document_generator = Agent(
    name="Document Generator",
    instructions="""あなたはテクニカルライターです。
    
    以下の形式でMarkdownドキュメントを生成してください：
    
    # プロジェクト計画書
    
    ## 1. プロジェクト概要
    - プロジェクトの目的と背景
    - 対象ユーザーと利害関係者
    - 期待される効果とKPI
    - プロジェクトスコープ
    
    ## 2. 要件定義
    ### 2.1 機能要件
    - コア機能の詳細
    - ユーザーストーリー
    - 画面遷移とユーザーフロー
    
    ### 2.2 非機能要件
    - パフォーマンス要件
    - セキュリティ要件
    - 可用性要件
    - スケーラビリティ要件
    
    ### 2.3 制約条件
    - 技術的制約
    - ビジネス制約
    - 法的要件と規制
    
    ## 3. システムアーキテクチャ
    ### 3.1 技術スタック
    - フロントエンド
    - バックエンド
    - インフラストラクチャ
    - 外部サービス
    
    ### 3.2 システム構成
    - コンポーネント図
    - デプロイメント構成
    - ネットワーク構成
    
    ### 3.3 データフロー
    - データモデル
    - APIインターフェース
    - セキュリティ設計
    
    ## 4. 開発計画
    ### 4.1 マイルストーン
    - フェーズごとの目標
    - 主要なデリバリー項目
    - チェックポイント
    
    ### 4.2 タスク一覧
    - 作業項目と見積もり
    - 担当者とロール
    - 依存関係
    
    ### 4.3 リスク管理
    - 特定されたリスク
    - 対応策
    - コンティンジェンシープラン
    
    ## 5. 付録
    ### 5.1 技術仕様
    - 詳細な技術スタック
    - API仕様
    - データベーススキーマ
    
    ### 5.2 運用管理
    - 監視計画
    - バックアップ戦略
    - インシデント対応
    
    ### 5.3 用語集
    
    これまでの会話履歴を基に、以下の点に注意して文書を作成してください：
    - 論理的な構造と明確な説明
    - 具体的な例示と図表の活用
    - 技術的な正確性
    - 実装者が理解しやすい記述
    - トレーサビリティの確保""",
    functions=[transfer_to_document_reviewer],
)

# Document Reviewer Agent
document_reviewer = Agent(
    name="Document Reviewer",
    instructions="""あなたは経験豊富なプロジェクトマネージャーとして、
    作成されたプロジェクト計画書を批判的にレビューします。
    
    以下の観点から改善点を指摘してください：
    
    1. 要件の明確性と完全性
    - 要件の具体性と測定可能性
    - 必須機能の網羅性
    - 非機能要件の充実度
    - ユーザーストーリーの妥当性
    - セキュリティ要件の十分性
    
    2. アーキテクチャの妥当性
    - 技術選定の根拠
    - スケーラビリティの考慮
    - セキュリティ設計の適切性
    - 保守性と拡張性
    - コスト効率
    - 運用面での実現可能性
    
    3. 開発計画の実現可能性
    - タスクの粒度と見積もりの適切性
    - 依存関係の明確性
    - リソース配分の妥当性
    - リスク対策の十分性
    - スケジュールの現実性
    
    4. ドキュメントの品質
    - 構造の論理性
    - 説明の十分性
    - 図表の効果的な使用
    - 用語の一貫性
    - トレーサビリティ
    
    5. プロジェクト全体の整合性
    - 目的とスコープの一致
    - 要件とアーキテクチャの整合性
    - コストと期間の妥当性
    - リスクと対策の適切性
    
    レビュー結果は以下の形式で提供してください：
    
    ### カテゴリー
    - **改善点**：具体的な問題点
    - **提案**：改善のための具体的な提案
    
    最後に、プロジェクトの成功に向けた総合的な提言を行ってください。""",
    functions=[],
)

# インタビューの質問定義
interview_questions = [
    {
        "phase": "プロジェクト概要",
        "questions": [
            "このプロジェクトの主な目的は何ですか？",
            "想定されるユーザーは誰ですか？",
            "プロジェクトの完了期限はありますか？",
            "プロジェクトの規模（予算、人員など）に制約はありますか？",
        ],
    },
    {
        "phase": "機能要件",
        "questions": [
            "必須として考えている機能を教えてください",
            "あったら良いと考えている追加機能はありますか？",
            "特に重視する非機能要件（性能、セキュリティなど）はありますか？",
            "既存のシステムやツールとの連携は必要ですか？",
        ],
    },
    {
        "phase": "技術的制約",
        "questions": [
            "使用したい特定の技術やフレームワークはありますか？",
            "開発環境や運用環境について制約はありますか？",
            "セキュリティに関する特別な要件はありますか？",
            "パフォーマンスに関する具体的な要件はありますか？",
        ],
    },
]


def get_multiline_input(prompt):
    """複数行の入力を受け付ける関数"""
    console.print(f"\n[bold]{prompt}[/bold]")
    console.print(
        "[dim](入力を終了するには、新しい行で 'done' を入力してください)[/dim]"
    )

    lines = []
    while True:
        try:
            line = input().strip()
            if line.lower() == "done":
                break
            lines.append(line)
        except EOFError:
            break
        except UnicodeDecodeError:
            console.print(
                "[red]入力文字列のエンコーディングエラーが発生しました。再度入力してください。[/red]"
            )
            continue

    return "\n".join(lines)


def run_requirement_interview():
    project_info = {}

    console.print(Panel.fit("プロジェクトヒアリングを開始します", style="bold green"))

    for phase in interview_questions:
        console.print(f"\n[bold blue]--- {phase['phase']} ---[/bold blue]")
        phase_answers = {}

        for question in phase["questions"]:
            answer = get_multiline_input(question)
            phase_answers[question] = answer

        project_info[phase["phase"]] = phase_answers

        # フェーズ完了確認
        if not questionary.confirm(
            f"{phase['phase']}のヒアリングが完了しました。次のフェーズに進みますか？",
            default=True,
        ).ask():
            # 修正オプションを提供
            while True:
                modify = questionary.select(
                    "修正したい質問を選択してください:",
                    choices=[*phase["questions"], "修正完了"],
                ).ask()

                if modify == "修正完了":
                    break

                new_answer = get_multiline_input(modify)
                phase_answers[modify] = new_answer

    return project_info


def format_project_description(project_info):
    description = "プロジェクト要件の詳細:\n\n"
    for phase, answers in project_info.items():
        description += f"【{phase}】\n"
        for question, answer in answers.items():
            description += f"・{question}\n  {answer}\n"
        description += "\n"
    return description


def run_with_loading(message, func, *args, **kwargs):
    """ローディング表示付きで関数を実行する"""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description=f"[bold blue]{message}...", total=None)
        return func(*args, **kwargs)


def run_development_planning_session(project_description):
    console.print(Panel.fit("プロジェクト開発計画セッション", style="bold green"))

    conversation = [{"role": "user", "content": project_description}]

    try:
        # フェーズ1: 要件分析
        console.print("\n[bold blue]=== フェーズ1: 要件分析 ===[/bold blue]")
        response = run_with_loading(
            "要件分析を実行中",
            client.run,
            agent=requirements_analyst,
            messages=conversation,
        )
        requirements = response.messages[-1]["content"]
        conversation.append({"role": "assistant", "content": requirements})
        console.print(Markdown(requirements))

        # 要件の確認と追加質問
        if questionary.confirm(
            "要件について追加の質問やclarificationが必要ですか？"
        ).ask():
            clarification = get_multiline_input("追加の情報を入力してください:")
            conversation.append({"role": "user", "content": clarification})
            response = run_with_loading(
                "追加の要件分析を実行中",
                client.run,
                agent=requirements_analyst,
                messages=conversation,
            )
            updated_requirements = response.messages[-1]["content"]
            conversation.append({"role": "assistant", "content": updated_requirements})
            console.print(Markdown(updated_requirements))

        # フェーズ2: アーキテクチャ設計
        console.print("\n[bold blue]=== フェーズ2: アーキテクチャ設計 ===[/bold blue]")
        response = run_with_loading(
            "アーキテクチャ設計を実行中",
            client.run,
            agent=architect,
            messages=conversation,
        )
        architecture = response.messages[-1]["content"]
        conversation.append({"role": "assistant", "content": architecture})
        console.print(Markdown(architecture))

        # アーキテクチャの確認
        if questionary.confirm(
            "アーキテクチャ設計について質問や懸念点はありますか？"
        ).ask():
            arch_feedback = get_multiline_input("フィードバックを入力してください:")
            conversation.append({"role": "user", "content": arch_feedback})
            response = run_with_loading(
                "アーキテクチャの更新を実行中",
                client.run,
                agent=architect,
                messages=conversation,
            )
            updated_architecture = response.messages[-1]["content"]
            conversation.append({"role": "assistant", "content": updated_architecture})
            console.print(Markdown(updated_architecture))

        # フェーズ3: タスク分解と計画
        console.print("\n[bold blue]=== フェーズ3: タスク分解と計画 ===[/bold blue]")
        response = run_with_loading(
            "タスク計画を作成中", client.run, agent=task_manager, messages=conversation
        )
        tasks = response.messages[-1]["content"]
        conversation.append({"role": "assistant", "content": tasks})
        console.print(Markdown(tasks))

        # タスク計画の確認
        if questionary.confirm("タスク計画について調整が必要な点はありますか？").ask():
            task_feedback = get_multiline_input("フィードバックを入力してください:")
            conversation.append({"role": "user", "content": task_feedback})
            response = run_with_loading(
                "タスク計画の更新を実行中",
                client.run,
                agent=task_manager,
                messages=conversation,
            )
            updated_tasks = response.messages[-1]["content"]
            conversation.append({"role": "assistant", "content": updated_tasks})
            console.print(Markdown(updated_tasks))

    except Exception as e:
        console.print(f"[bold red]エラーが発生しました: {str(e)}[/bold red]")

    return conversation


def generate_markdown_document(conversation_history):
    console.print("\n[bold blue]=== ドキュメント生成フェーズ ===[/bold blue]")

    response = run_with_loading(
        "ドキュメントを生成中",
        client.run,
        agent=document_generator,
        messages=conversation_history,
    )
    document = response.messages[-1]["content"]

    # ドキュメントの保存
    with open("project_plan.md", "w", encoding="utf-8") as f:
        f.write(document)

    console.print("[green]ドキュメントを生成しました: project_plan.md[/green]")
    return document


def review_document(document):
    console.print("\n[bold blue]=== ドキュメントレビューフェーズ ===[/bold blue]")

    review_request = {
        "role": "user",
        "content": f"以下のプロジェクト計画書をレビューしてください：\n\n{document}",
    }

    response = run_with_loading(
        "レビューを実行中",
        client.run,
        agent=document_reviewer,
        messages=[review_request],
    )
    review = response.messages[-1]["content"]

    # レビュー結果の保存
    with open("document_review.md", "w", encoding="utf-8") as f:
        f.write(review)

    console.print("[green]レビュー結果を生成しました: document_review.md[/green]")
    return review


def main():
    console.print(Panel.fit("プロジェクト計画支援システム", style="bold green"))

    # プロジェクトヒアリングの実施
    project_info = run_requirement_interview()

    # ヒアリング結果の確認
    console.print("\n[bold]収集した情報の確認[/bold]")
    console.print(Markdown(format_project_description(project_info)))

    if questionary.confirm("この内容で開発計画フェーズに進みますか？").ask():
        # 開発計画セッションの実行
        conversation_history = run_development_planning_session(
            format_project_description(project_info)
        )

        # ドキュメント生成
        document = generate_markdown_document(conversation_history)

        # レビュー
        review = review_document(document)

        # 結果の表示
        console.print(
            Panel.fit(
                "プロセス完了\n\n生成されたファイル:\n1. project_plan.md\n2. document_review.md",
                style="bold green",
            )
        )
    else:
        console.print("[yellow]プロセスを中断しました[/yellow]")


if __name__ == "__main__":
    main()
