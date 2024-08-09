#!/bin/bash
commit_msg_file="$1"
commit_msg=$(cat "$commit_msg_file")

if ! grep -q "If applied, my commit will:" "$commit_msg_file"; then
    echo "Error: A mensagem de commit deve incluir a seção 'If applied, my commit will:'"
    exit 1
fi

if ! grep -q "What I did was:" "$commit_msg_file"; then
    echo "Error: A mensagem de commit deve incluir a seção 'What I did was:'"
    exit 1
fi

if ! grep -q "Severidade:" "$commit_msg_file"; then
    echo "Error: A mensagem de commit deve incluir a seção 'Severidade:'"
    exit 1
fi
