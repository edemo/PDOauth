from test.helpers.PDUnitTest import PDUnitTest, test
from pdoauth.Observable import Observable

class TestObservable(Observable):
    pass

class TestObserver(object):
    eventFired = False
    @classmethod
    def eventHandler(cls, arg):
        cls.eventFired = True

class ObserverTest(PDUnitTest):

    @test
    def observer_functions_can_be_subscribed_for_an_event(self):
        TestObservable.subscribe(TestObserver.eventHandler,"event")

    @test
    def when_an_observable_emits_an_event_the_observer_gets_fired(self):
        TestObservable.subscribe(TestObserver.eventHandler, "event")
        observable = TestObservable()
        observable.notify("event")
        self.assertTrue(TestObserver.eventFired)
 