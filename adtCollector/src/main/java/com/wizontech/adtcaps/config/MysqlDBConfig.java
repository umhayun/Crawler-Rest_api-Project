package com.wizontech.adtcaps.config;

import javax.sql.DataSource;

import org.apache.ibatis.session.SqlSessionFactory;
import org.mybatis.spring.SqlSessionFactoryBean;
import org.mybatis.spring.SqlSessionTemplate;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.support.PathMatchingResourcePatternResolver;
import org.springframework.stereotype.Component;

import com.zaxxer.hikari.HikariDataSource;

@Configuration
@Component
public class MysqlDBConfig {
    @Bean(name = "firstDataSource")
    @ConfigurationProperties(prefix = "spring.datasource.hikari")
    public DataSource firstDataSource() {

        return new HikariDataSource();
    }

    @Bean(name = "firstSqlSessionFactory")
    public SqlSessionFactory firstSqlSessionFactory(@Qualifier("firstDataSource") DataSource dataSource)
            throws Exception {
        SqlSessionFactoryBean sqlSessionFactoryBean = new SqlSessionFactoryBean();
        sqlSessionFactoryBean.setDataSource(dataSource);
        sqlSessionFactoryBean.setMapperLocations(
                new PathMatchingResourcePatternResolver().getResources("classpath:/mybatis/**/*.xml"));

        return sqlSessionFactoryBean.getObject();
    }

    @Bean(name = "firstSqlSessionTemplate")
    public SqlSessionTemplate firstSqlSessionTemplate(
            @Qualifier("firstSqlSessionFactory") SqlSessionFactory sqlSessionFactory) {

        return new SqlSessionTemplate(sqlSessionFactory);
    }
}