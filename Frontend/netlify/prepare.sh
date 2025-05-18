#!/bin/bash

# Installer pnpm
npm install -g pnpm@9.12.3

# Nettoyer le cache et les modules
rm -rf node_modules
rm -rf .nuxt
rm -rf .output

# Installer les dépendances sans frozen-lockfile
pnpm install --no-frozen-lockfile 