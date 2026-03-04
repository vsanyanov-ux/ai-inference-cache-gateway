terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.0.1"
    }
  }
}

provider "docker" {}

resource "docker_network" "app_network" {
  name = "ai_cache_network"
}

resource "docker_image" "postgres" {
  name = "postgres:15-alpine"
}

resource "docker_container" "db" {
  name  = "ai_cache_db"
  image = docker_image.postgres.image_id
  networks_advanced {
    name = docker_network.app_network.name
  }
  env = [
    "POSTGRES_USER=postgres",
    "POSTGRES_PASSWORD=postgres",
    "POSTGRES_DB=ai_cache"
  ]
  ports {
    internal = 5432
    external = 5432
  }
}

resource "docker_image" "redis" {
  name = "redis:7-alpine"
}

resource "docker_container" "redis_cache" {
  name  = "ai_cache_redis"
  image = docker_image.redis.image_id
  networks_advanced {
    name = docker_network.app_network.name
  }
  ports {
    internal = 6379
    external = 6379
  }
}
