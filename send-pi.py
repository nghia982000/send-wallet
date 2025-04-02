import aiohttp
import asyncio

DISCORD_WEBHOOK_URL = "https://discord.com/api/v10/webhooks/1341617810287099964/oDyQM4PaOgceJWjOaESSPTmCYEi4_bqm4ZCpeKrTCSDt59w0Jqxou7cFggN1xCFRxsNt"


async def get_account_balance(session, account_id):
    url = f"https://api.mainnet.minepi.com/accounts/{account_id}"
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            data = await response.json()

            balances = data.get("balances", [])
            for balance in balances:
                if balance.get("asset_type") == "native":
                    balance_value = float(balance.get("balance", 0))
                    if balance_value > 2:
                        return f"Tài khoản: {account_id} - Số dư: {balance_value} Pi"

            return None  # Không gửi nếu số dư <= 2
    except Exception as e:
        return f"⚠️ Lỗi khi gọi API cho {account_id}: {e}"


async def send_to_discord(results):
    results = [res for res in results if res]  # Lọc bỏ kết quả None
    if not results:
        print("⚠️ Không có kết quả nào để gửi.")
        return

    message = "\n".join(results)
    payload = {"content": f"```{message}```"}  # Định dạng trong block code

    async with aiohttp.ClientSession() as session:
        async with session.post(DISCORD_WEBHOOK_URL, json=payload) as response:
            if response.status == 204:
                print("✅ Đã gửi kết quả lên Discord")
            else:
                print(f"⚠️ Lỗi khi gửi lên Discord: {response.status}")


async def check_all_balances(file_path="address-wallet.txt"):
    account_ids = load_account_ids(file_path)

    async with aiohttp.ClientSession() as session:
        tasks = [get_account_balance(session, account_id) for account_id in account_ids]
        results = await asyncio.gather(*tasks)

    for result in results:
        if result:
            print(result)

    await send_to_discord(results)


def load_account_ids(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f.readlines() if line.strip()]


if __name__ == "__main__":
    asyncio.run(check_all_balances("address-pi-lock.txt"))
