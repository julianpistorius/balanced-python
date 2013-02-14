"""
Welcome weary traveller. Sick of polling for state changes? Well today have I
got good news for you. Run this example below to see how to get yourself some
callback goodness and to understand how events work.
"""
from __future__ import unicode_literals
import time

import balanced

from helpers import RequestBinClient


def init():
    key = balanced.APIKey().save()
    balanced.configure(key.secret)
    balanced.Marketplace().save()


def main():
    init()
    request_bin = RequestBinClient()

    print 'let\'s create a callback'
    balanced.Callback(
        url=request_bin.callback_url,
    ).save()

    print 'let\'s create a card and associate it with a new account'
    card = balanced.Card(
        expiration_month='12',
        security_code='123',
        card_number='5105105105105100',
        expiration_year='2020',
    ).save()
    buyer = balanced.Account(
        card_uri=card.uri,
    ).save()

    print 'generate a debit (which implicitly creates and captures a hold)'
    buyer.debit(100)

    print 'event creation is an async operation, let\'s wait until we have ' \
          'some events!'
    while not balanced.Event.query.count():
        print 'Zzzz'
        time.sleep(0)

    print 'Woop, we got some events, let us see what there is to look at'
    for event in balanced.Event.query:
        print 'this was a {} event, is occurred at {}, the callback has a ' \
              'status of {}'.format(
            event.type,
            event.occurred_at,
            event.callback_statuses
        )

    print 'you can inspect each event to see the logs'
    event = balanced.Event.query[0]
    for callback in event.callbacks:
        print 'inspecting callback to {} for event {}'.format(
            callback.url,
            event.type,
        )
        for log in callback.logs:
            print 'this attempt to the callback {}'.format(log.status)

    print 'ok, let\'s check with requestb.in to see if our callbacks fired'
    print 'we received {} callbacks, you can view them at {}'.format(
        len(request_bin.get_requests()),
        request_bin.view_url,
    )


if __name__ == '__main__':
    main()
