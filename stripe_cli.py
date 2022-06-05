import os, docker, logging, asgiref.sync
logger = logging.getLogger(__name__)

if not 'STRIPE_API_SECRET' in os.environ.keys():
    os.environ.setdefault('STRIPE_API_SECRET', 'sk_test_51KbRPhBlXqCTWmcH0ByNRrTQgKwsodAmpUfReugFtuxeAtMBe4ABVab2gaNvbDzGMAsnJcG1ANcZ8PcHnNI0c4Co00eRdg7s1O')

if not 'PROJECT_NETWORK' in os.environ.keys():
    os.environ.setdefault('PROJECT_NETWORK', 'global_project_network')


def run_stripe_cli_container():
    try:
        STRIPE_API_SECRET = os.environ.get('STRIPE_API_SECRET')
        PROJECT_NETWORK = os.environ.get('PROJECT_NETWORK')

        client = docker.from_env(version='1.41')
        client.containers.run(image='stripe/stripe-cli',
        command=" listen --api-key " + STRIPE_API_SECRET + " --forward-to "\
        "http://0.0.0.0:8082/webhook/payment/ --events payment_intent.succeeded,payment_intent.failed",
        network=PROJECT_NETWORK
        )


    except(docker.errors.NotFound,):
        logger.error('STRIPE CLI CONTAINER HAS BEEN DELETED. ')


run_stripe_cli_container()




