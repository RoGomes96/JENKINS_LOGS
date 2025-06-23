import asyncio

from jenkins_log.controller.jenkins_logs import processar_logs_jenkins

if __name__ == "__main__":
    asyncio.run(processar_logs_jenkins())
