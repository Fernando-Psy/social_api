def test_cloudinary_config():
    """Testa a configuração do Cloudinary"""
    print("\n🔧 TESTANDO CONFIGURAÇÃO DO CLOUDINARY")
    print("=" * 50)

    try:
        from django.conf import settings

        print(f"✓ DEBUG mode: {settings.DEBUG}")

        if settings.DEBUG:
            # Modo desenvolvimento - usando sistema de arquivos local
            print("\n⚠️  MODO DESENVOLVIMENTO (DEBUG=True)")
            print("✓ Usando sistema de arquivos local para uploads")
            print(f"✓ MEDIA_ROOT: {settings.MEDIA_ROOT}")
            print(f"✓ MEDIA_URL: {settings.MEDIA_URL}")
            return True

        else:
            # Modo produção - usando Cloudinary
            print("\n⚡ MODO PRODUÇÃO (DEBUG=False)")

            # Verifica se CLOUDINARY_STORAGE existe
            if hasattr(settings, 'CLOUDINARY_STORAGE') and settings.CLOUDINARY_STORAGE:
                config = settings.CLOUDINARY_STORAGE
                print(f"✓ Configuração CLOUDINARY_STORAGE encontrada")
                print(f"✓ CLOUD_NAME: {config.get('CLOUD_NAME', 'Não definido')}")
                print(f"✓ API_KEY: {'✓ Definido' if config.get('API_KEY') else '✗ Não definido'}")
                print(f"✓ API_SECRET: {'✓ Definido' if config.get('API_SECRET') else '✗ Não definido'}")

                # Verifica se as credenciais estão presentes
                if config.get('CLOUD_NAME') and config.get('API_KEY') and config.get('API_SECRET'):
                    return True
                else:
                    print("\n✗ Credenciais do Cloudinary incompletas")
                    return False
            else:
                print("\n✗ CLOUDINARY_STORAGE não configurado")
                return False

    except Exception as e:
        print(f"\n✗ Erro ao verificar configuração: {str(e)}")
        return False