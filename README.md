# Boca no Trombone: Aplicação Web para Conscientização Social 🗣️

https://bocanotrombone-flax.vercel.app/

Este projeto é uma aplicação web desenvolvida em Python com Flask, utilizando MySQL como banco de dados, que visa fortalecer a comunicação entre a população e a gestão pública municipal, proporcionando um canal direto para reportar problemas e acompanhar ações de resolução. 🤝

## Funcionalidades Detalhadas ✨

### Formulário de Reclamações:
Permite aos cidadãos reportar problemas, especificando a localização (bairro, rua, cidade), a categoria do problema e fornecendo uma descrição detalhada. 📝

### Dashboard Interativo:
Exibe informações relevantes sobre as reclamações registradas, incluindo:

- **Mapa de Calor:** Visualização espacial das ocorrências, permitindo identificar áreas com maior concentração de problemas. 🗺️🔥
- **Nuvem de Palavras:** Destaca os termos mais frequentes nas descrições dos problemas, evidenciando as principais preocupações da população. ☁️
- **Últimos Casos Submetidos:** Tabela com as cinco reclamações mais recentes, incluindo data, rua, bairro e tipo de problema, garantindo transparência e acesso à informação. 📰
- **Contagem de Reclamações Abertas:** Gráfico de barras que quantifica as reclamações por categoria, fornecendo uma visão geral dos problemas mais recorrentes. 📊

### Funcionalidade de Encerramento de Ticket:
Permite que a gestão pública marque as reclamações como resolvidas, demonstrando a resolução de problemas e fomentando a confiança da população. ✅

## Melhorias de Performance Implementadas 🚀

- **AJAX para Submissão de Formulários:** Assegura uma experiência de usuário mais fluida e rápida, evitando o recarregamento completo da página após o envio de formulários. ⚡
- **Dropdown Dinâmico de Ruas:** Otimiza a seleção de ruas no formulário, carregando apenas as opções relevantes com base no bairro escolhido, agilizando o preenchimento. 🏙️
- **Armazenamento de Dados Geográficos:** Inclui latitude e longitude para cada rua, permitindo a construção do Mapa de Calor e facilitando futuras análises espaciais. 📍

## Próximos Passos e Considerações ⏭️

- **Autenticação de Usuários:** Implementar um sistema de login para diferenciar usuários (cidadãos e gestores públicos), permitindo ações específicas para cada perfil. 🔐
- **Sistema de Notificações:** Notificar os cidadãos sobre o andamento de suas reclamações, aumentando a interação e o engajamento com a plataforma. 🔔
- **Painel de Controle Administrativo:** Criar uma interface dedicada à gestão pública para acompanhar as reclamações, gerenciar o status de resolução e gerar relatórios. 💼

## Conclusão 🎉

A aplicação "Boca no Trombone" representa um passo significativo na construção de uma cidade mais participativa, transparente e eficiente, colocando o cidadão no centro do processo de resolução de problemas e promovendo a melhoria da qualidade de vida da população. 🌟
