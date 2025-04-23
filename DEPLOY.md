# Instruções para Implantação do Serviço Docling

Este documento contém instruções para implantar o serviço Docling no servidor ifva.duckdns.org.

## Pré-requisitos

- Acesso SSH ao servidor
- Docker e Docker Compose instalados no servidor
- Permissões para configurar o Nginx

## Passos para Implantação

### 1. Transferir os arquivos para o servidor

```bash
# Exemplo usando scp (ajuste o usuário e caminho conforme necessário)
scp -r ./* usuario@ifva.duckdns.org:/home/ifsul/servicos/docling/
```

### 2. Configurar o Nginx

1. Copie o arquivo de configuração do Nginx para o diretório de configurações:

```bash
sudo cp /home/ifsul/servicos/docling/nginx/docling.conf /home/ifsul/configs/
sudo cp /home/ifsul/configs/docling.conf /etc/nginx/conf.d/apps/
```

2. Verifique a configuração do Nginx:

```bash
sudo nginx -t
```

3. Se a configuração estiver correta, recarregue o Nginx:

```bash
sudo systemctl reload nginx
```

### 3. Iniciar o serviço Docling

1. Navegue até o diretório do projeto:

```bash
cd /home/ifsul/servicos/docling/
```

2. Inicie os containers Docker:

```bash
./run.sh start
```

Se encontrar problemas de timeout durante a construção da imagem, use a opção de timeout estendido:

```bash
./run.sh build-timeout
./run.sh start
```

3. Verifique se os containers estão em execução:

```bash
./run.sh status
```

4. Verifique os logs para garantir que tudo está funcionando corretamente:

```bash
./run.sh logs
```

### 4. Verificar a implantação

1. Acesse a documentação da API para verificar se o serviço está funcionando:

```
https://ifva.duckdns.org/docling/docs
```

2. Teste a API enviando um documento para processamento.

## Manutenção

### Atualizar o serviço

Para atualizar o serviço após alterações no código:

```bash
cd /home/ifsul/servicos/docling/
git pull  # Se estiver usando controle de versão
./run.sh build
./run.sh restart
```

### Monitorar logs

Para monitorar os logs do serviço:

```bash
./run.sh logs
```

### Parar o serviço

Para parar o serviço:

```bash
./run.sh stop
```

## Solução de Problemas

### Verificar status dos containers

```bash
docker ps
```

### Verificar logs do Nginx

```bash
sudo tail -f /var/log/nginx/error.log
```

### Reiniciar o Nginx

```bash
sudo systemctl restart nginx
```

### Verificar portas em uso

```bash
sudo netstat -tulpn | grep 8082
```
