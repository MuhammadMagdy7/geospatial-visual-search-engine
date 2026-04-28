FROM pgvector/pgvector:pg16

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/*.list 2>/dev/null || true && \
    apt-get update && apt-get install -y postgresql-16-postgis-3 \
    && rm -rf /var/lib/apt/lists/*