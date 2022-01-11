import factory

from common_amirainvest_com.utils.decorators import get_async_session


class FactoryBase(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        sqlalchemy_session = None
        sqlalchemy_session_persistence = None

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """
        Doing all of this by hand because:
        1) No async async_session support https://github.com/FactoryBoy/factory_boy/issues/679
        2) The async_session is not created when this file is imported, so you have to call get_session at creation time
        """
        async_session = get_async_session()

        # cls._meta.sqlalchemy_session = get_session()
        # sqlalchemy_object = super(FactoryBase, cls)._create(model_class, *args, **kwargs)

        async def wait():
            obj = model_class(*args, **kwargs)
            async_session.add(obj)

            await async_session.commit()
            # https://docs.sqlalchemy.org/en/14/orm/extensions/asyncio.html#preventing-implicit-io-when-using-asyncsession
            await async_session.refresh(obj)

            return obj
            # await cls._meta.sqlalchemy_session.commit()
            # return sqlalchemy_object

        return wait()
