from website import start_app
app = start_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
