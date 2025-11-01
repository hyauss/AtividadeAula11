import requests
import threading
import time

# A URL do Serviço de Agendamento (Flask)
# Certifique-se de que o Flask esteja rodando nesta porta.
URL_AGENDAMENTO = "http://127.0.0.1:5000/agendamentos"

# Número de requisições simultâneas
NUMERO_DE_REQUISICOES = 10

# Os dados EXATOS que todas as requisições tentarão criar.
# É crucial que seja o mesmo payload para forçar a condição de corrida.
PAYLOAD_CONFLITANTE = {
    "cientista_id": 1,
    "horario_inicio_utc": "2025-12-01T03:00:00Z"
    # Adicione outros campos necessários conforme seu MODELOS.md
}


def fazer_requisicao_agendamento(thread_num):
    """
    Função que será executada por cada thread.
    Ela envia uma única requisição POST para o endpoint de agendamento.
    """
    print(f"[Thread {thread_num}]: Iniciando requisição...")

    try:
        response = requests.post(URL_AGENDAMENTO, json=PAYLOAD_CONFLITANTE)
        print(f"[Thread {thread_num}]: Resposta recebida! "
              f"Status Code: {response.status_code}, "
              f"Body: {response.text[:100]}...")

    except requests.exceptions.ConnectionError as e:
        print(f"[Thread {thread_num}]: Erro de conexão. "
              f"O servidor Flask está rodando? Erro: {e}")
    except Exception as e:
        print(f"[Thread {thread_num}]: Erro inesperado: {e}")


if __name__ == "__main__":
    print(f"Disparando {NUMERO_DE_REQUISICOES} requisições simultâneas para {URL_AGENDAMENTO}")
    print(f"Payload: {PAYLOAD_CONFLITANTE}\n")

    threads = []
    start_time = time.time()

    for i in range(NUMERO_DE_REQUISICOES):
        t = threading.Thread(target=fazer_requisicao_agendamento, args=(i + 1,))
        threads.append(t)
        t.start()

    # Aguarda todas as threads terminarem
    for t in threads:
        t.join()

    elapsed_time = time.time() - start_time
    print(f"\nTodas as requisições finalizadas em {elapsed_time:.2f} segundos.")
