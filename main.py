from agent import DeepSeekAgent

def main():
    agent = DeepSeekAgent()
    print("=== DeepSeek 最小单 Agent CLI ===")
    print("输入 q / quit / exit 退出，输入 /reset 重置上下文。")

    while True:
        user_input = input("\n你：").strip()
        if user_input.lower() in {"q", "quit", "exit"}:
            print("已退出。")
            break
        if user_input == "/reset":
            agent.reset()
            print("上下文已重置。")
            continue
        if not user_input:
            continue

        answer = agent.run(user_input)
        print("\nAgent：", answer)

if __name__ == "__main__":
    main()
